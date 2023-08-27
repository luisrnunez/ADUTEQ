from django.db import connection
from django.db import migrations


def verifica_y_crea_funcion_informe(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'obtener_datos_socios')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
                CREATE OR REPLACE FUNCTION public.nuevo_obtener_datos(
                    socio integer,
                    mes integer,
                    anio integer)
                RETURNS TABLE(nombre text, cedula character varying, cuota_prestamos numeric, aportacion numeric, descuento_proveedores numeric, aportacion_ayudaseco numeric, total numeric) 
                LANGUAGE 'plpgsql'
                COST 100
                VOLATILE PARALLEL UNSAFE
                ROWS 1000

                AS $BODY$
                BEGIN
                    RETURN QUERY
                    SELECT
                        CONCAT(u.first_name, ' ', u.last_name) AS nombre,
                        s.cedula AS cedula,
                        SUM(COALESCE(dc.valor_cuota, 0)) AS cuota_prestamos,
                        SUM(COALESCE(sa.aportacion_total, 0)) AS aportacion,
                        SUM(COALESCE(p.consumo_total, 0)) AS descuento_proveedores,
                        SUM(COALESCE(ae.valor, 0)) AS aportacion_ayudaseco,
                        SUM(COALESCE(pm.monto_pago, 0) + COALESCE(sa.aportacion_total, 0) + COALESCE(p.consumo_total, 0) + COALESCE(ae.valor, 0) + COALESCE(dc.valor_cuota, 0)) AS total
                    FROM
                        public.socios_socios s
                    INNER JOIN
                        public.auth_user u ON s.user_id = u.id
                    LEFT JOIN (
                        SELECT socio_id, SUM(monto_pago) AS monto_pago
                        FROM public."Prestamos_pagomensual"
                        WHERE EXTRACT(MONTH FROM fecha_pago) = mes AND EXTRACT(YEAR FROM fecha_pago) = anio AND socio_id = socio
                        GROUP BY socio_id
                    ) pm ON s.id = pm.socio_id
                    LEFT JOIN (
                        SELECT socio_id, SUM(monto) AS aportacion_total
                        FROM public.socios_aportaciones
                        WHERE EXTRACT(MONTH FROM fecha) = mes AND EXTRACT(YEAR FROM fecha) = anio AND socio_id = socio
                        GROUP BY socio_id
                    ) sa ON s.id = sa.socio_id
                    LEFT JOIN (
                        SELECT pa.socio_id, SUM(pa.consumo_total) AS consumo_total
                        FROM public."Pagos_pagos" pa
                        WHERE EXTRACT(MONTH FROM pa.fecha_consumo) = mes AND EXTRACT(YEAR FROM pa.fecha_consumo) = anio AND pa.socio_id = socio
                        GROUP BY pa.socio_id
                    ) p ON s.id = p.socio_id
                    LEFT JOIN (
                        SELECT pc.socio_id, SUM(pc.valor_cuota) AS valor_cuota
                        FROM public."Pagos_pagos_cuotas" pc
                        INNER JOIN public."Pagos_detalle_cuotas" dc ON pc.id = dc.pago_cuota_id
                        WHERE EXTRACT(MONTH FROM dc.fecha_descuento) = mes AND EXTRACT(YEAR FROM dc.fecha_descuento) = anio AND pc.socio_id = socio
                        GROUP BY pc.socio_id
                    ) dc ON s.id = dc.socio_id
                    LEFT JOIN (
                        SELECT socio_id, SUM(valor) AS valor
                        FROM public.ayudas_econ_detallesayuda
                        WHERE EXTRACT(MONTH FROM fecha) = mes AND EXTRACT(YEAR FROM fecha) = anio AND socio_id = socio
                        GROUP BY socio_id
                    ) ae ON s.id = ae.socio_id
                    WHERE s.id = socio  -- Filtrar por el socio específico
                    GROUP BY
                        CONCAT(u.first_name, ' ', u.last_name),
                        s.cedula
                    ORDER BY
                        1,
                        2;
                END;
                $BODY$;
                """
            )


def verifica_y_crea_funcion_comsumos_proveedor(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'obtener_consumos_por_proveedor')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
                CREATE OR REPLACE FUNCTION obtener_consumos_por_proveedor(id_socio bigint, numero_mes integer, anio integer)
                RETURNS TABLE (
                    proveedor_nombre character varying(200),
                    consumo_total numeric
                )
                AS $$
                BEGIN
                    RETURN QUERY
                    SELECT pr.nombre AS proveedor_nombre, SUM(pa.consumo_total) AS consumo_total
                    FROM public."Pagos_pagos" pa
                    INNER JOIN public.proveedores_proveedor pr ON pa.proveedor_id = pr.id
                    WHERE pa.socio_id = id_socio
                        AND EXTRACT(MONTH FROM pa.fecha_consumo) = numero_mes
                        AND EXTRACT(YEAR FROM pa.fecha_consumo) = anio
                    GROUP BY pr.nombre;
                    
                    RETURN QUERY
                    SELECT 'Total'::character varying(200) AS proveedor_nombre, SUM(pa.consumo_total) AS montoa
                    FROM public."Pagos_pagos" pa
                    INNER JOIN public.proveedores_proveedor pr ON pa.proveedor_id = pr.id
                    WHERE pa.socio_id = id_socio
                        AND EXTRACT(MONTH FROM pa.fecha_consumo) = numero_mes
                        AND EXTRACT(YEAR FROM pa.fecha_consumo) = anio;
                END;
                $$ LANGUAGE plpgsql;
                """
            )


def verifica_y_crea_funcion_comsumos_cuotas(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'obtener_cuotas_pagadas')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
                CREATE OR REPLACE FUNCTION obtener_cuotas_pagadas(id_socio bigint, numero_mes integer, anio integer)
                RETURNS TABLE (
                    fecha date,
                    proveedor_nombre character varying(200),
                    numero_cuota integer,
                    valor_cuota numeric
                )
                AS $$
                BEGIN
                    RETURN QUERY
                    SELECT pc.fecha_descuento ,pr.nombre AS proveedor_nombre, pc.cuota_actual, pc.valor_cuota
                    FROM public."Pagos_pagos_cuotas" pc
                    INNER JOIN public.proveedores_proveedor pr ON pc.proveedor_id = pr.id
                    INNER JOIN public."Pagos_detalle_cuotas" dc ON pc.id = dc.pago_cuota_id
                    WHERE pc.socio_id = id_socio
                        AND EXTRACT(MONTH FROM dc.fecha_descuento) = numero_mes
                        AND EXTRACT(YEAR FROM dc.fecha_descuento) = anio;
                        
                    RETURN QUERY
                    SELECT NOW() ::date as fecha, 'Total'::character varying(200) AS proveedor_nombre, 0 as numero_cuota , SUM(pc.valor_cuota) AS montoa
                    FROM public."Pagos_pagos_cuotas" pc
                    INNER JOIN public.proveedores_proveedor pr ON pc.proveedor_id = pr.id
                    INNER JOIN public."Pagos_detalle_cuotas" dc ON pc.id = dc.pago_cuota_id
                    WHERE pc.socio_id = id_socio
                        AND EXTRACT(MONTH FROM dc.fecha_descuento) = numero_mes
                        AND EXTRACT(YEAR FROM dc.fecha_descuento) = anio;
                END;
                $$ LANGUAGE plpgsql;
                """
            )


def verifica_y_crea_funcion_aportaciones(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'obtener_aportacion_socio')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
               CREATE OR REPLACE FUNCTION obtener_aportacion_socio(id_socio bigint, numero_mes integer, anio integer)
                RETURNS TABLE (
                    tipo_aportacionn character varying(10),
                    montoa numeric
                )
                AS $$
                BEGIN
                    RETURN QUERY
                    SELECT tipo_aportacion, monto
                    FROM public.socios_aportaciones
                    WHERE socio_id = id_socio
                        AND EXTRACT(MONTH FROM fecha) = numero_mes
                        AND EXTRACT(YEAR FROM fecha) = anio;

                    -- Agregar el total calculado como una fila adicional
                    RETURN QUERY
                    SELECT 'Total'::character varying(10) AS tipo_aportacionn, SUM(monto) AS montoa
                    FROM public.socios_aportaciones
                    WHERE socio_id = id_socio
                        AND EXTRACT(MONTH FROM fecha) = numero_mes
                        AND EXTRACT(YEAR FROM fecha) = anio
                    GROUP BY tipo_aportacionn;
                END;
                $$ LANGUAGE plpgsql;
                """
            )


def verifica_y_crea_funcion_ayudas(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'obtener_info_ayuda_economica')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
                CREATE OR REPLACE FUNCTION public.obtener_info_ayuda_economica(
                    id_socio bigint,
                    numero_mes integer,
                    anio integer)
                RETURNS TABLE(descripcion text, valor_aportado numeric) 
                LANGUAGE 'plpgsql'
                COST 100
                VOLATILE PARALLEL UNSAFE
                ROWS 1000
                AS $BODY$
                BEGIN
                    RETURN QUERY
                    SELECT ae.descripcion, da.valor
                    FROM public.ayudas_econ_ayudaseconomicas ae
                    INNER JOIN public.ayudas_econ_detallesayuda da ON ae.id = da.ayuda_id
                    WHERE da.socio_id = id_socio
                        AND EXTRACT(MONTH FROM ae.fecha) = numero_mes
                        AND EXTRACT(YEAR FROM ae.fecha) = anio
                        AND EXTRACT(MONTH FROM da.fecha) = numero_mes
                        AND EXTRACT(YEAR FROM da.fecha) = anio;

                    -- Agregar fila "total"
                    RETURN QUERY
                    SELECT 'Total' AS descripcion, SUM(da.valor) AS monto
                    FROM public.ayudas_econ_detallesayuda da
                    WHERE da.socio_id = id_socio
                        AND EXTRACT(MONTH FROM (SELECT fecha FROM public.ayudas_econ_ayudaseconomicas WHERE id = da.ayuda_id)) = numero_mes
                        AND EXTRACT(YEAR FROM (SELECT fecha FROM public.ayudas_econ_ayudaseconomicas WHERE id = da.ayuda_id)) = anio
                        AND EXTRACT(MONTH FROM da.fecha) = numero_mes
                        AND EXTRACT(YEAR FROM da.fecha) = anio
                        AND da.cancelado = true;
                END;
                $BODY$;
                """
            )


def verifica_y_crea_funcion_generar_pdf(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'obtener_informe_mensual')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
                CREATE OR REPLACE FUNCTION public.obtener_informe_mensual(
                    id_socio bigint,
                    numero_mes integer,
                    anio integer)
                RETURNS TABLE(columna1 character varying, columna2 numeric) 
                LANGUAGE 'plpgsql'
                COST 100
                VOLATILE PARALLEL UNSAFE
                ROWS 1000
                AS $BODY$
                DECLARE
                    total numeric := 0;
                BEGIN
                    -- Crear tabla temporal para almacenar los resultados de la subconsulta
                    CREATE TEMP TABLE temp_result AS
                    SELECT proveedor_nombre, valor, orden FROM (
                        SELECT proveedor_nombre, consumo_total as valor, 1 as orden FROM (
                            SELECT pr.nombre AS proveedor_nombre, SUM(pa.consumo_total) AS consumo_total
                            FROM public."Pagos_pagos" pa
                            INNER JOIN public.proveedores_proveedor pr ON pa.proveedor_id = pr.id
                            WHERE pa.socio_id = id_socio
                                AND EXTRACT(MONTH FROM pa.fecha_consumo) = numero_mes
                                AND EXTRACT(YEAR FROM pa.fecha_consumo) = anio
                            GROUP BY pr.nombre
                        ) cp
                        UNION ALL
                        SELECT proveedor_nombre, valor_cuota, 2 as orden FROM (
                            SELECT pc.fecha_descuento AS fecha_cuota, pr.nombre AS proveedor_nombre, pc.valor_cuota AS valor_cuota
                            FROM public."Pagos_pagos_cuotas" pc
                            INNER JOIN public.proveedores_proveedor pr ON pc.proveedor_id = pr.id
                            INNER JOIN public."Pagos_detalle_cuotas" dc ON pc.id = dc.pago_cuota_id
                            WHERE pc.socio_id = id_socio
                                AND EXTRACT(MONTH FROM dc.fecha_descuento) = numero_mes
                                AND EXTRACT(YEAR FROM dc.fecha_descuento) = anio
                        ) cu
                        UNION ALL
                        SELECT tipo_aportacion, montoa_aportacion, 3 as orden FROM (
                            SELECT sa.tipo_aportacion, sa.monto AS montoa_aportacion
                            FROM public.socios_aportaciones sa
                            WHERE sa.socio_id = id_socio
                                AND EXTRACT(MONTH FROM sa.fecha) = numero_mes
                                AND EXTRACT(YEAR FROM sa.fecha) = anio
                        ) ap
                        UNION ALL
                        SELECT descripcion, valor_aportado, 4 as orden FROM (
                            SELECT ae.descripcion, da.valor AS valor_aportado
                            FROM public.ayudas_econ_ayudaseconomicas ae
                            INNER JOIN public.ayudas_econ_detallesayuda da ON ae.id = da.ayuda_id
                            WHERE da.socio_id = id_socio
                                AND EXTRACT(MONTH FROM ae.fecha) = numero_mes
                                AND EXTRACT(YEAR FROM ae.fecha) = anio
                                AND EXTRACT(MONTH FROM da.fecha) = numero_mes
                                AND EXTRACT(YEAR FROM da.fecha) = anio
                                AND da.cancelado = true
                        ) ae
                    ) AS subquery;

                    -- Calcular la suma total desde la tabla temporal
                    SELECT SUM(valor) INTO total FROM temp_result;

                    -- Devolver los resultados de la subconsulta
                    RETURN QUERY
                    SELECT proveedor_nombre, valor FROM temp_result
                    ORDER BY orden, proveedor_nombre;

                    -- Agregar fila "Total"
                    RETURN QUERY
                    SELECT 'Total'::character varying as columna1, total as columna2;
                    
                    -- Eliminar la tabla temporal al finalizar
                    DROP TABLE IF EXISTS temp_result;
                END;
                $BODY$;
                """
            )


def actualizar_cancelados(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'actualizar_cancelados')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
                CREATE OR REPLACE FUNCTION public.actualizar_cancelados(
                    mes integer,
                    anio integer,
                    socio integer)
                    RETURNS void
                    LANGUAGE 'plpgsql'
                    COST 100
                    VOLATILE PARALLEL UNSAFE
                AS $BODY$
                                BEGIN
                                    UPDATE public."Prestamos_pagomensual"
                                    SET cancelado = True
                                    WHERE EXTRACT(MONTH FROM fecha_pago) = mes AND EXTRACT(YEAR FROM fecha_pago) = anio
                                    and socio_id=socio;
                                END;
                                
                $BODY$;
                """
            )

def actualizar_estados(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'actualizar_estados')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
                CREATE OR REPLACE FUNCTION public.actualizar_estados(
                    mes integer,
                    anio integer,
                    socio integer)
                    RETURNS void
                    LANGUAGE 'plpgsql'
                    COST 100
                    VOLATILE PARALLEL UNSAFE
                AS $BODY$
                                BEGIN
                                    UPDATE public."Pagos_detalle_cuotas"
                                    SET estado = True
                                    WHERE EXTRACT(MONTH FROM fecha_descuento) = mes AND EXTRACT(YEAR FROM fecha_descuento) = anio
                                    and socio_id=socio;
                                END;
                                
                $BODY$;
                """
            )

def obtener_ayudas_func(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'obtener_ayudas_func')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
                CREATE OR REPLACE FUNCTION public.obtener_ayudas_func(
                    mes integer,
                    anio integer)
                    RETURNS TABLE(nombre text, cedula character varying, fecha_ayuda date, aportacion_ayudaseco numeric) 
                    LANGUAGE 'plpgsql'
                    COST 100
                    VOLATILE PARALLEL UNSAFE
                    ROWS 1000

                AS $BODY$
                BEGIN
                    RETURN QUERY
                    SELECT
                        CONCAT(u.first_name, ' ', u.last_name) AS Nombre,
                        s.cedula AS cedula,
                        ae.fecha AS fecha,
                        SUM(COALESCE(ae.valor, 0)) AS aportacion_ayudaseco
                    FROM
                        public.socios_socios s
                    INNER JOIN
                        public.auth_user u ON s.user_id = u.id
                    LEFT JOIN (
                        SELECT socio_id, fecha, SUM(valor) AS valor
                        FROM public.ayudas_econ_detallesayuda
                        WHERE EXTRACT(MONTH FROM fecha) = mes AND EXTRACT(YEAR FROM fecha) = anio
                        GROUP BY socio_id, fecha
                    ) ae ON s.id = ae.socio_id
                    GROUP BY
                        u.first_name, u.last_name, s.cedula, ae.fecha
                    HAVING SUM(COALESCE(ae.valor, 0)) > 0;
                END;
                $BODY$;
                """
            )

def obtener_consumo_total_func(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'obtener_consumo_total_func')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
                CREATE OR REPLACE FUNCTION public.obtener_consumo_total_func(
                    mes integer,
                    anio integer)
                    RETURNS TABLE(nombre text, cedula character varying, cuota_prestamos numeric, cuota_descuento numeric, aportacion numeric, descuento_proveedores numeric, aportacion_ayudaseco numeric, total numeric) 
                    LANGUAGE 'plpgsql'
                    COST 100
                    VOLATILE PARALLEL UNSAFE
                    ROWS 1000

                AS $BODY$
                                BEGIN
                                    RETURN QUERY
                                    SELECT
                                        CONCAT(u.last_name, ' ', u.first_name) AS Nombre,
                                        s.cedula AS cedula,
                                        SUM(COALESCE(pm.monto_pago, 0)) AS cuota_prestamos,
                                        SUM(COALESCE(pd.valor_cuota, 0)) AS cuota_descuento,
                                        SUM(COALESCE(sa.aportacion_total, 0)) AS aportacion,
                                        SUM(COALESCE(p.consumo_total, 0)) AS descuento_proveedores,
                                        SUM(COALESCE(ae.valor, 0)) AS aportacion_ayudaseco,
                                        SUM(COALESCE(pm.monto_pago, 0) + COALESCE(pd.valor_cuota, 0) + COALESCE(sa.aportacion_total, 0) + COALESCE(p.consumo_total, 0) 
                                            + COALESCE(ae.valor, 0)) AS consumo_total
                                    FROM
                                        public.socios_socios s
                                    INNER JOIN
                                        public.auth_user u ON s.user_id = u.id
                                    LEFT JOIN (
                                        SELECT socio_id, SUM(monto) AS aportacion_total
                                        FROM public.socios_aportaciones
                                        WHERE EXTRACT(MONTH FROM fecha) = mes AND EXTRACT(YEAR FROM fecha) = anio
                                        GROUP BY socio_id
                                    ) sa ON s.id = sa.socio_id
                                    LEFT JOIN (
                                        SELECT socio_id, SUM(consumo_total) AS consumo_total
                                        FROM public."Pagos_pagos"
                                        WHERE EXTRACT(MONTH FROM fecha_consumo) = mes AND EXTRACT(YEAR FROM fecha_consumo) = anio
                                        GROUP BY socio_id
                                    ) p ON s.id = p.socio_id
                                    LEFT JOIN (
                                        SELECT socio_id, SUM(monto_pago) AS monto_pago
                                        FROM public."Prestamos_pagomensual"
                                        WHERE EXTRACT(MONTH FROM fecha_pago) = mes AND EXTRACT(YEAR FROM fecha_pago) = anio 
                                        and cancelado = False
                                        GROUP BY socio_id
                                    ) pm ON s.id = pm.socio_id
                                    
                                    LEFT JOIN (
                                        SELECT socio_id, SUM(valor_cuota) AS valor_cuota
                                        FROM public."Pagos_detalle_cuotas"
                                        WHERE EXTRACT(MONTH FROM fecha_descuento) = mes AND EXTRACT(YEAR FROM fecha_descuento) = anio 
                                        and estado = False
                                        GROUP BY socio_id
                                    ) pd ON s.id = pd.socio_id
                                    
                                    LEFT JOIN (
                                        SELECT socio_id, SUM(valor) AS valor
                                        FROM public.ayudas_econ_detallesayuda
                                        WHERE EXTRACT(MONTH FROM fecha) = mes AND EXTRACT(YEAR FROM fecha) = anio
                                        GROUP BY socio_id
                                    ) ae ON s.id = ae.socio_id
                                    GROUP BY
                                        u.first_name, u.last_name, s.cedula
                                        HAVING SUM(COALESCE(pm.monto_pago, 0) + COALESCE(pd.valor_cuota, 0) + COALESCE(sa.aportacion_total, 0) + COALESCE(p.consumo_total, 0) 
                                            + COALESCE(ae.valor, 0))>0
                                        ORDER BY u.last_name;
                                END;
                                
                $BODY$;
                """
            )

def obtener_consumos_proveedores_func(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'obtener_consumos_proveedores_func')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
                CREATE OR REPLACE FUNCTION public.obtener_consumos_proveedores_func(
                    mes integer,
                    anio integer)
                    RETURNS TABLE(nombre text, cedula character varying, fecha date, descuento_proveedores numeric) 
                    LANGUAGE 'plpgsql'
                    COST 100
                    VOLATILE PARALLEL UNSAFE
                    ROWS 1000

                AS $BODY$
                                BEGIN
                                    RETURN QUERY
                                    SELECT
                                        CONCAT(u.first_name, ' ', u.last_name) AS Nombre,
                                        s.cedula AS cedula,
                                        p.fecha_consumo,
                                        SUM(COALESCE(p.consumo_total, 0)) AS descuento_proveedores
                                    FROM
                                        public.socios_socios s
                                    INNER JOIN
                                        public.auth_user u ON s.user_id = u.id
                                    LEFT JOIN (
                                        SELECT socio_id, fecha_consumo,SUM(consumo_total) AS consumo_total
                                        FROM public."Pagos_pagos"
                                        WHERE EXTRACT(MONTH FROM fecha_consumo) = mes AND EXTRACT(YEAR FROM fecha_consumo) = anio
                                        GROUP BY socio_id, fecha_consumo
                                    ) p ON s.id = p.socio_id
                                    GROUP BY
                                        u.first_name, u.last_name, s.cedula, p.fecha_consumo
                                    HAVING SUM(COALESCE(p.consumo_total, 0)) > 0;
                                END;
                                
                $BODY$;
                """
            )

def obtener_cuota_descuentos_func(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'obtener_cuota_descuentos_func')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
                CREATE OR REPLACE FUNCTION public.obtener_cuota_descuentos_func(
                    mes integer,
                    anio integer)
                    RETURNS TABLE(nombre text, cedula character varying, fecha date, cuota_descuento numeric, id_socio bigint) 
                    LANGUAGE 'plpgsql'
                    COST 100
                    VOLATILE PARALLEL UNSAFE
                    ROWS 1000

                AS $BODY$
                                BEGIN
                                    RETURN QUERY
                                    SELECT
                                        CONCAT(u.first_name, ' ', u.last_name) AS Nombre,
                                        s.cedula AS cedula,
                                        pd.fecha_descuento,
                                        SUM(COALESCE(pd.valor_cuota, 0)) AS cuota_descuento,
                                        s.id
                                    FROM
                                        public.socios_socios s
                                    INNER JOIN
                                        public.auth_user u ON s.user_id = u.id
                                    LEFT JOIN (
                                        SELECT socio_id, fecha_descuento, SUM(valor_cuota) AS valor_cuota
                                        FROM public."Pagos_detalle_cuotas"
                                        WHERE EXTRACT(MONTH FROM fecha_descuento) = mes AND EXTRACT(YEAR FROM fecha_descuento) = anio 
                                        AND estado = False
                                        GROUP BY socio_id, fecha_descuento
                                    ) pd ON s.id = pd.socio_id
                                    GROUP BY
                                        u.first_name, u.last_name, s.cedula, pd.fecha_descuento,s.id
                                    HAVING SUM(COALESCE(pd.valor_cuota, 0)) > 0;
                                END;
                                
                $BODY$;
                """
            )

def obtener_cuota_prestamos_func(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'obtener_cuota_prestamos_func')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
                CREATE OR REPLACE FUNCTION public.obtener_cuota_prestamos_func(
                    mes integer,
                    anio integer)
                    RETURNS TABLE(nombre text, cedula character varying, fecha date, cuota_prestamos numeric, id_socio bigint) 
                    LANGUAGE 'plpgsql'
                    COST 100
                    VOLATILE PARALLEL UNSAFE
                    ROWS 1000

                AS $BODY$
                BEGIN
                    RETURN QUERY
                    SELECT
                        CONCAT(u.first_name, ' ', u.last_name) AS Nombre,
                        s.cedula AS cedula,
                        pm.fecha_pago,
                        SUM(COALESCE(pm.monto_pago, 0)) AS cuota_prestamos,
                        s.id
                    FROM
                        public.socios_socios s
                    INNER JOIN
                        public.auth_user u ON s.user_id = u.id
                    LEFT JOIN (
                        SELECT socio_id, fecha_pago, SUM(monto_pago) AS monto_pago
                        FROM public."Prestamos_pagomensual"
                        WHERE EXTRACT(MONTH FROM fecha_pago) = mes AND EXTRACT(YEAR FROM fecha_pago) = anio 
                        AND cancelado = False
                        GROUP BY socio_id, fecha_pago
                    ) pm ON s.id = pm.socio_id
                    GROUP BY
                        u.first_name, u.last_name, s.cedula, pm.fecha_pago,s.id
                    HAVING SUM(COALESCE(pm.monto_pago, 0)) > 0;
                END;
                $BODY$;
                """
            )

def obtener_suma_ayudas_func(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'obtener_suma_ayudas_func')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
                CREATE OR REPLACE FUNCTION public.obtener_suma_ayudas_func(
                    mes integer,
                    anio integer)
                    RETURNS numeric
                    LANGUAGE 'plpgsql'
                    COST 100
                    VOLATILE PARALLEL UNSAFE
                AS $BODY$
                DECLARE
                    total_pago numeric;
                BEGIN
                    SELECT SUM(valor) INTO total_pago
                    FROM public.ayudas_econ_detallesayuda
                    WHERE EXTRACT(MONTH FROM fecha) = mes AND EXTRACT(YEAR FROM fecha) = anio;
                    RETURN total_pago;
                END;
                $BODY$;
                """
            )

def obtener_suma_consumo_total_descuentos_func(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'obtener_suma_consumo_total_descuentos_func')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
                CREATE OR REPLACE FUNCTION public.obtener_suma_consumo_total_descuentos_func(
                    mes integer,
                    anio integer)
                    RETURNS numeric
                    LANGUAGE 'plpgsql'
                    COST 100
                    VOLATILE PARALLEL UNSAFE
                AS $BODY$
                DECLARE
                    suma_consumo numeric;
                BEGIN
                    SELECT SUM(consumo_total) INTO suma_consumo
                    FROM public."Pagos_pagos"
                    WHERE EXTRACT(MONTH FROM fecha_consumo) = mes AND EXTRACT(YEAR FROM fecha_consumo) = anio;

                    RETURN suma_consumo;
                END;
                $BODY$;
                """
            )

def obtener_suma_descuento_cuotas_func(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'obtener_suma_descuento_cuotas_func')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
                CREATE OR REPLACE FUNCTION public.obtener_suma_descuento_cuotas_func(
                    mes integer,
                    anio integer)
                    RETURNS numeric
                    LANGUAGE 'plpgsql'
                    COST 100
                    VOLATILE PARALLEL UNSAFE
                AS $BODY$
                DECLARE
                    total_pago numeric;
                BEGIN
                    SELECT SUM(valor_cuota) INTO total_pago
                    FROM public."Pagos_detalle_cuotas"
                    WHERE EXTRACT(MONTH FROM fecha_descuento) = mes AND EXTRACT(YEAR FROM fecha_descuento) = anio
                    and estado=False;

                    RETURN total_pago;
                END;
                $BODY$;
                """
            )

def obtener_suma_prestamo_total_func(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'obtener_suma_prestamo_total_func')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
                CREATE OR REPLACE FUNCTION public.obtener_suma_prestamo_total_func(
                    mes integer,
                    anio integer)
                    RETURNS numeric
                    LANGUAGE 'plpgsql'
                    COST 100
                    VOLATILE PARALLEL UNSAFE
                AS $BODY$
                DECLARE
                    total_pago numeric;
                BEGIN
                    SELECT SUM(monto_pago) INTO total_pago
                    FROM public."Prestamos_pagomensual"
                    WHERE EXTRACT(MONTH FROM fecha_pago) = mes AND EXTRACT(YEAR FROM fecha_pago) = anio
                    and cancelado=False;

                    RETURN total_pago;
                END;
                $BODY$;
                """
            )

class Migration(migrations.Migration):

    dependencies = [
        # Otras dependencias de migración
    ]

    operations = [
        migrations.RunPython(verifica_y_crea_funcion_informe),
        migrations.RunPython(verifica_y_crea_funcion_comsumos_proveedor),
        migrations.RunPython(verifica_y_crea_funcion_comsumos_cuotas),
        migrations.RunPython(verifica_y_crea_funcion_aportaciones),
        migrations.RunPython(verifica_y_crea_funcion_ayudas),
        migrations.RunPython(verifica_y_crea_funcion_generar_pdf),
        migrations.RunPython(actualizar_cancelados),
        migrations.RunPython(actualizar_estados),
        migrations.RunPython(obtener_ayudas_func),
        migrations.RunPython(obtener_consumo_total_func),
        migrations.RunPython(obtener_consumos_proveedores_func),
        migrations.RunPython(obtener_cuota_descuentos_func),
        migrations.RunPython(obtener_cuota_prestamos_func),
        migrations.RunPython(obtener_suma_ayudas_func),
        migrations.RunPython(obtener_suma_consumo_total_descuentos_func),
        migrations.RunPython(obtener_suma_descuento_cuotas_func),
        migrations.RunPython(obtener_suma_prestamo_total_func),
    ]
