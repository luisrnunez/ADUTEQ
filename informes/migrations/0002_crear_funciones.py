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
    RETURNS TABLE(nombre text, cedula character varying, cuota_cuotas numeric, cuota_prestamo numeric, aportacion numeric, descuento_proveedores numeric, aportacion_ayudaseco numeric, total numeric) 
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
                        SUM(COALESCE(dc.valor_cuota, 0)) AS cuota_cuotas,
						SUM(COALESCE(pm.monto_pago, 0)) AS cuota_prestamo,
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

def actualizar_descuentos(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'actualizar_descuentos')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
               CREATE OR REPLACE FUNCTION public.actualizar_descuentos(
                    mes integer,
                    anio integer,
                    cedu character varying)
                    RETURNS void
                    LANGUAGE 'plpgsql'
                    COST 100
                    VOLATILE PARALLEL UNSAFE
                AS $BODY$
                                BEGIN
                                    UPDATE public."Pagos_pagos" p
                                    SET estado = True
                                    FROM public.socios_socios s
                                    WHERE p.socio_id = s.id
                                        AND EXTRACT(MONTH FROM p.fecha_consumo) = mes
                                        AND EXTRACT(YEAR FROM p.fecha_consumo) = anio
                                        AND s.cedula = cedu;
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
                    cedu character varying)
                    RETURNS void
                    LANGUAGE 'plpgsql'
                    COST 100
                    VOLATILE PARALLEL UNSAFE
                AS $BODY$
                                                BEGIN
                                                    UPDATE public."Pagos_detalle_cuotas" pd
                                                    SET estado = True
													FROM public.socios_socios s
                                                    WHERE pd.socio_id = s.id
                                        			AND EXTRACT(MONTH FROM pd.fecha_descuento) = mes
                                        			AND EXTRACT(YEAR FROM pd.fecha_descuento) = anio
                                        			AND s.cedula = cedu;
                                                END;
                                                
                                
                
                $BODY$;
                """
            )

def actualizar_estados_ayudas(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'actualizar_estados_ayudas')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
                CREATE OR REPLACE FUNCTION public.actualizar_estados_ayudas(
                    mes integer,
                    anio integer,
                    id_ayuda integer)
                    RETURNS void
                    LANGUAGE 'plpgsql'
                    COST 100
                    VOLATILE PARALLEL UNSAFE
                AS $BODY$
                                                BEGIN
                                                    UPDATE public.ayudas_econ_detallesayuda
                                                    SET pagado = True
                                                    where id=id_ayuda;
                                                END;
                                                
                                
                $BODY$;
                """
            )

def actualizar_estados_ayudas_exter(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'actualizar_estados_ayudas_exter')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
                CREATE OR REPLACE FUNCTION public.actualizar_estados_ayudas_exter(
                    mes integer,
                    anio integer,
                    id_ayuda integer)
                    RETURNS void
                    LANGUAGE 'plpgsql'
                    COST 100
                    VOLATILE PARALLEL UNSAFE
                AS $BODY$
                                                                BEGIN
                                                                    UPDATE public.ayudas_econ_ayudasexternas
                                                                    SET estado = True
                                                                    where id=id_ayuda;
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
                    RETURNS TABLE(nombre text, cedula character varying, fecha_ayuda date, aportacion_ayudaseco numeric, id_ayuda bigint) 
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
                                        SUM(COALESCE(ae.valor, 0)) AS aportacion_ayudaseco,
                                        ae.id
                                    FROM
                                        public.socios_socios s
                                    INNER JOIN
                                        public.auth_user u ON s.user_id = u.id
                                    LEFT JOIN (
                                        SELECT socio_id, fecha, SUM(valor) AS valor, id
                                        FROM public.ayudas_econ_detallesayuda
                                        WHERE EXTRACT(MONTH FROM fecha) = mes AND EXTRACT(YEAR FROM fecha) = anio
                                        and pagado=False
                                        GROUP BY socio_id, fecha, id
                                    ) ae ON s.id = ae.socio_id
                                    GROUP BY
                                        u.first_name, u.last_name, s.cedula, ae.fecha, ae.id
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
                                                                        and estado = False
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
                                                                        and pagado = False
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

def obtener_consumo_total_todos_func(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'obtener_consumo_total_todos_func')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
                CREATE OR REPLACE FUNCTION public.obtener_consumo_total_todos_func(
                    mes integer,
                    anio integer)
                    RETURNS TABLE(nombre text, cedula character varying, cuota_prestamos numeric, cuota_descuento numeric, aportacion numeric, descuento_proveedores numeric, aportacion_ayudaseco numeric, total numeric, todas_cumplidas boolean) 
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
                                        SUM(COALESCE(pm.monto_pago, 0) + COALESCE(pd.valor_cuota, 0) + COALESCE(sa.aportacion_total, 0) + COALESCE(p.consumo_total, 0) + COALESCE(ae.valor, 0)) AS consumo_total,
                                        (SUM(CASE WHEN COALESCE(pd.estado, true) AND COALESCE(pm.cancelado, true) AND COALESCE(ae.pagado, true) AND COALESCE(p.estado, true) THEN 1 ELSE 0 END) = COUNT(*)) AS todas_cumplidas
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
                                        SELECT socio_id, SUM(consumo_total) AS consumo_total, estado
                                        FROM public."Pagos_pagos"
                                        WHERE EXTRACT(MONTH FROM fecha_consumo) = mes AND EXTRACT(YEAR FROM fecha_consumo) = anio
                                        GROUP BY socio_id, estado
                                    ) p ON s.id = p.socio_id
                                    LEFT JOIN (
                                        SELECT socio_id, SUM(monto_pago) AS monto_pago, cancelado
                                        FROM public."Prestamos_pagomensual"
                                        WHERE EXTRACT(MONTH FROM fecha_pago) = mes AND EXTRACT(YEAR FROM fecha_pago) = anio 
                                        GROUP BY socio_id, cancelado
                                    ) pm ON s.id = pm.socio_id
                                                                    
                                    LEFT JOIN (
                                        SELECT socio_id, SUM(valor_cuota) AS valor_cuota, estado
                                        FROM public."Pagos_detalle_cuotas"
                                        WHERE EXTRACT(MONTH FROM fecha_descuento) = mes AND EXTRACT(YEAR FROM fecha_descuento) = anio 
                                        GROUP BY socio_id, estado
                                    ) pd ON s.id = pd.socio_id
                                                                    
                                    LEFT JOIN (
                                        SELECT socio_id, SUM(valor) AS valor, pagado
                                        FROM public.ayudas_econ_detallesayuda
                                        WHERE EXTRACT(MONTH FROM fecha) = mes AND EXTRACT(YEAR FROM fecha) = anio
                                        GROUP BY socio_id, pagado
                                    ) ae ON s.id = ae.socio_id
                                    GROUP BY
                                        u.first_name, u.last_name, s.cedula
                                    HAVING SUM(COALESCE(pm.monto_pago, 0) + COALESCE(pd.valor_cuota, 0) + COALESCE(sa.aportacion_total, 0) + COALESCE(p.consumo_total, 0) + COALESCE(ae.valor, 0)) > 0
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
                    RETURNS TABLE(nombre text, cedula character varying, descuento_proveedores numeric) 
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
                                        SUM(COALESCE(p.consumo_total, 0)) AS descuento_proveedores
                                    FROM
                                        public.socios_socios s
                                    INNER JOIN
                                        public.auth_user u ON s.user_id = u.id
                                    LEFT JOIN (
                                        SELECT socio_id, SUM(consumo_total) AS consumo_total
                                        FROM public."Pagos_pagos"
                                        WHERE EXTRACT(MONTH FROM fecha_consumo) = mes AND EXTRACT(YEAR FROM fecha_consumo) = anio
                                        AND estado = False
                                        GROUP BY socio_id
                                    ) p ON s.id = p.socio_id
                                    GROUP BY
                                        u.first_name, u.last_name, s.cedula
                                    HAVING SUM(COALESCE(p.consumo_total, 0)) > 0
                                    order by u.last_name;
                                END;
                                
                $BODY$;
                """
            )

def obtener_consumos_por_proveedor_detalle_cuotas(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'obtener_consumos_por_proveedor_detalle_cuotas')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
                CREATE OR REPLACE FUNCTION public.obtener_consumos_por_proveedor_detalle_cuotas(
                    id_socio bigint,
                    numero_mes integer,
                    anio integer)
                    RETURNS TABLE(proveedor_nombre character varying, consumo_total numeric) 
                    LANGUAGE 'plpgsql'
                    COST 100
                    VOLATILE PARALLEL UNSAFE
                    ROWS 1000

                AS $BODY$
                BEGIN
                    RETURN QUERY
                    SELECT pr.nombre AS proveedor_nombre, SUM(dc.valor_cuota) AS consumo_total
                    FROM public."Pagos_detalle_cuotas" dc
                    INNER JOIN public.proveedores_proveedor pr ON dc.proveedor_id = pr.id
                    WHERE dc.socio_id = id_socio
                        AND EXTRACT(MONTH FROM dc.fecha_descuento) = numero_mes
                        AND EXTRACT(YEAR FROM dc.fecha_descuento) = anio
                    GROUP BY pr.nombre;
                    
                    RETURN QUERY
                    SELECT 'Total'::character varying(200) AS proveedor_nombre, SUM(dc.valor_cuota) AS monto
                    FROM public."Pagos_detalle_cuotas" dc
                    INNER JOIN public.proveedores_proveedor pr ON dc.proveedor_id = pr.id
                    WHERE dc.socio_id = id_socio
                        AND EXTRACT(MONTH FROM dc.fecha_descuento) = numero_mes
                        AND EXTRACT(YEAR FROM dc.fecha_descuento) = anio;
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
                    RETURNS TABLE(nombres text, cedula character varying, fecha date, cuota_descuento numeric, id_socio bigint, proveedor character varying) 
                    LANGUAGE 'plpgsql'
                    COST 100
                    VOLATILE PARALLEL UNSAFE
                    ROWS 1000

                AS $BODY$
                                                BEGIN
                                                    RETURN QUERY
                                                    SELECT
                                                        CONCAT(u.last_name, ' ', u.first_name) AS Nombres,
                                                        s.cedula AS cedula,
                                                        pd.fecha_descuento,
                                                        SUM(COALESCE(pd.valor_cuota, 0)) AS cuota_descuento,
                                                        pd.id,
                                                        pr.nombre
                                                    FROM
                                                        public.socios_socios s
                                                    INNER JOIN
                                                        public.auth_user u ON s.user_id = u.id
                                                    LEFT JOIN (
                                                        SELECT socio_id, fecha_descuento, SUM(valor_cuota) AS valor_cuota, id, proveedor_id
                                                        FROM public."Pagos_detalle_cuotas"
                                                        WHERE EXTRACT(MONTH FROM fecha_descuento) = mes AND EXTRACT(YEAR FROM fecha_descuento) = anio 
                                                        AND estado = False
                                                        GROUP BY socio_id, fecha_descuento,id
                                                    ) pd ON s.id = pd.socio_id
                                                    LEFT JOIN(select nombre, id 
                                                    from public.proveedores_proveedor) pr on pd.proveedor_id = pr.id
                                                    GROUP BY
                                                        u.first_name, u.last_name, s.cedula, pd.fecha_descuento, pd.id,pr.nombre
                                                    HAVING SUM(COALESCE(pd.valor_cuota, 0)) > 0
                                                    order by u.last_name;
                                                END;
                                                
                                
                $BODY$;
                """
            )

def obtener_cuota_descuentos_total_func(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'obtener_cuota_descuentos_total_func')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
                CREATE OR REPLACE FUNCTION public.obtener_cuota_descuentos_total_func(
                    mes integer,
                    anio integer)
                    RETURNS TABLE(nombres text, cedula character varying, fecha date, cuota_descuento_total numeric) 
                    LANGUAGE 'plpgsql'
                    COST 100
                    VOLATILE PARALLEL UNSAFE
                    ROWS 1000

                AS $BODY$
                BEGIN
                    RETURN QUERY
                    SELECT
                        CONCAT(u.last_name, ' ', u.first_name) AS Nombres,
                        s.cedula AS cedula,
                        pd.fecha_descuento,
                        SUM(COALESCE(pd.valor_cuota, 0)) AS cuota_descuento_total
                    FROM
                        public.socios_socios s
                    INNER JOIN
                        public.auth_user u ON s.user_id = u.id
                    LEFT JOIN (
                        SELECT socio_id, fecha_descuento, SUM(valor_cuota) AS valor_cuota
                        FROM public."Pagos_detalle_cuotas"
                        WHERE EXTRACT(MONTH FROM fecha_descuento) = mes 
                        AND EXTRACT(YEAR FROM fecha_descuento) = anio 
                        AND estado = False
                        GROUP BY socio_id, fecha_descuento
                    ) pd ON s.id = pd.socio_id
                    GROUP BY
                        u.first_name, u.last_name, s.cedula, pd.fecha_descuento
                    HAVING SUM(COALESCE(pd.valor_cuota, 0)) > 0
                    ORDER BY u.last_name;
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
                                        CONCAT(u.last_name, ' ', u.first_name) AS Nombre,
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
                                    HAVING SUM(COALESCE(pm.monto_pago, 0)) > 0
                                    order by u.last_name;
                                END;
                                
                $BODY$;
                """
            )

def obtener_aportaciones_externas_func(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'obtener_aportaciones_externas_func')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
                CREATE OR REPLACE FUNCTION public.obtener_aportaciones_externas_func(
                    mes integer,
                    anio integer)
                    RETURNS TABLE(nombres text, cedulas text, fecha_aportacion date, aportacion numeric, id_ayuda bigint) 
                    LANGUAGE 'plpgsql'
                    COST 100
                    VOLATILE PARALLEL UNSAFE
                    ROWS 1000

                AS $BODY$
                                        BEGIN
                                            RETURN QUERY
                                            SELECT
                                                nombre,
                                                cedula,
                                                fecha,
                                                SUM(COALESCE(valor, 0)) AS aportacion,
                                                id
                                                FROM public.ayudas_econ_ayudasexternas
                                                WHERE EXTRACT(MONTH FROM fecha) = mes AND EXTRACT(YEAR FROM fecha) = anio
                                                and estado=False
                                            GROUP BY
                                                nombre, cedula, fecha, id
                                            HAVING SUM(COALESCE(valor, 0)) > 0;
                                        END;         
                $BODY$;
                """
            )

def obtener_suma_aportaciones_externas_func(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'obtener_suma_aportaciones_externas_func')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
                CREATE OR REPLACE FUNCTION public.obtener_suma_aportaciones_externas_func(
                    mes integer,
                    anio integer)
                    RETURNS numeric
                    LANGUAGE 'plpgsql'
                    COST 100
                    VOLATILE PARALLEL UNSAFE
                AS $BODY$
                                                DECLARE
                                                    suma_ayuext numeric;
                                                BEGIN
                                                    SELECT SUM(valor) INTO suma_ayuext
                                                    FROM public.ayudas_econ_ayudasexternas
                                                    WHERE EXTRACT(MONTH FROM fecha) = mes AND EXTRACT(YEAR FROM fecha) = anio
                                                    and estado = false;

                                                    RETURN suma_ayuext;
                                                END;
                                                
                                
                $BODY$;
                """
            )

def obtener_suma_aportaciones_func(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'obtener_suma_aportaciones_func')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
                CREATE OR REPLACE FUNCTION public.obtener_suma_aportaciones_func(
                    mes integer,
                    anio integer)
                    RETURNS numeric
                    LANGUAGE 'plpgsql'
                    COST 100
                    VOLATILE PARALLEL UNSAFE
                AS $BODY$
                DECLARE
                    total_aportaciones numeric;
                BEGIN
                    SELECT SUM(monto) INTO total_aportaciones
                    FROM public.socios_aportaciones
                    WHERE EXTRACT(MONTH FROM fecha) = mes AND EXTRACT(YEAR FROM fecha) = anio;
                    RETURN total_aportaciones;
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
                                    WHERE EXTRACT(MONTH FROM fecha) = mes AND EXTRACT(YEAR FROM fecha) = anio
                                    and pagado=False;
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
                                                    WHERE EXTRACT(MONTH FROM fecha_consumo) = mes AND EXTRACT(YEAR FROM fecha_consumo) = anio
                                                    and estado = False;

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

def obtener_suma_prestamo_total_pagados_func(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'obtener_suma_prestamo_total_pagados_func')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
                CREATE OR REPLACE FUNCTION public.obtener_suma_prestamo_total_pagados_func(
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
                                                    and cancelado=True;

                                                    RETURN total_pago;
                                                END;
                                                
                                
                $BODY$;
                """
            )

def obtener_suma_total(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'obtener_suma_total')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
                CREATE OR REPLACE FUNCTION public.obtener_suma_total(
                    mes integer,
                    anio integer)
                    RETURNS numeric
                    LANGUAGE 'plpgsql'
                    COST 100
                    VOLATILE PARALLEL UNSAFE
                AS $BODY$
                                                DECLARE
                                                    total NUMERIC;
                                                    total_ayudas NUMERIC;
                                                    total_descuentos NUMERIC;
                                                    descuento_cuotas NUMERIC;
                                                    total_pres NUMERIC;
                                                    total_aport NUMERIC;
                                                BEGIN
                                                    total := 0;
                                                    total_ayudas := 0;
                                                    total_descuentos := 0;
                                                    descuento_cuotas := 0;
                                                    total_pres := 0;
                                                    total_aport:=0;

                                                    SELECT COALESCE(SUM(valor), 0)
                                                    INTO total_ayudas
                                                    FROM public.ayudas_econ_detallesayuda
                                                    WHERE EXTRACT(MONTH FROM fecha) = mes AND EXTRACT(YEAR FROM fecha) = anio;

                                                    SELECT COALESCE(SUM(consumo_total), 0)
                                                    INTO total_descuentos
                                                    FROM public."Pagos_pagos"
                                                    WHERE EXTRACT(MONTH FROM fecha_consumo) = mes AND EXTRACT(YEAR FROM fecha_consumo) = anio;

                                                    SELECT COALESCE(SUM(valor_cuota), 0)
                                                    INTO descuento_cuotas
                                                    FROM public."Pagos_detalle_cuotas"
                                                    WHERE EXTRACT(MONTH FROM fecha_descuento) = mes AND EXTRACT(YEAR FROM fecha_descuento) = anio;

                                                    SELECT COALESCE(SUM(monto_pago), 0)
                                                    INTO total_pres
                                                    FROM public."Prestamos_pagomensual"
                                                    WHERE EXTRACT(MONTH FROM fecha_pago) = mes AND EXTRACT(YEAR FROM fecha_pago) = anio;
                                                    
                                                    SELECT COALESCE(SUM(monto), 0)
                                                    INTO total_aport
                                                    FROM public.socios_aportaciones
                                                    WHERE EXTRACT(MONTH FROM fecha) = mes AND EXTRACT(YEAR FROM fecha) = anio;

                                                    total := total_ayudas + total_descuentos + descuento_cuotas + total_pres + total_aport;

                                                    RETURN total;
                                                END;
                                                
                                
                $BODY$;
                """
            )

def total_des_pen(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'total_des_pen')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
                CREATE OR REPLACE FUNCTION public.total_des_pen(
                    mes integer,
                    anio integer,
                    id_socio integer)
                    RETURNS numeric
                    LANGUAGE 'plpgsql'
                    COST 100
                    VOLATILE PARALLEL UNSAFE
                AS $BODY$
                DECLARE
                    total1 numeric;
                    total2 numeric;
                BEGIN
                    total1 := 0;
                    total2 := 0;
                    SELECT 
                        COALESCE(SUM(consumo_total), 0) INTO total1
                    FROM 
                        public."Pagos_pagos_pendientes"
                    WHERE 
                        EXTRACT(MONTH FROM fecha_consumo) = mes 
                        AND EXTRACT(YEAR FROM fecha_consumo) = anio
                        AND estado = FALSE 
                        AND socio_id = id_socio;
                    SELECT 
                        COALESCE(SUM(valor_cuota), 0) INTO total2
                    FROM 
                        public."Pagos_detalle_cuotas_pendientes"
                    WHERE 
                        EXTRACT(MONTH FROM fecha_descuento) = mes 
                        AND EXTRACT(YEAR FROM fecha_descuento) = anio
                        AND estado = FALSE 
                        AND socio_id = id_socio;
                    RETURN total1+total2;
                END;
                $BODY$;
                """
            )

def obtener_informe_mensual2(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'obtener_informe_mensual2')")
        function_exists = cursor.fetchone()[0]

        if not function_exists:
            cursor.execute(
                """
                CREATE OR REPLACE FUNCTION public.obtener_informe_mensual2(
                    id_socio bigint,
                    numero_mes integer,
                    anio integer)
                    RETURNS TABLE(columna1 character varying, columna2 numeric, columna3 date, columna4 character varying) 
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
                                    SELECT proveedor_nombre, valor, fecha_transaccion, tipo_transaccion FROM (
                                        SELECT proveedor_nombre, consumo_total as valor, fecha_consumo as fecha_transaccion, 'Pago Consumo Proveedor'::character varying as tipo_transaccion, 1 as orden FROM (
                                            SELECT pr.nombre AS proveedor_nombre, SUM(pa.consumo_total) AS consumo_total, MAX(pa.fecha_consumo) as fecha_consumo
                                            FROM public."Pagos_pagos" pa
                                            INNER JOIN public.proveedores_proveedor pr ON pa.proveedor_id = pr.id
                                            WHERE pa.socio_id = id_socio
                                                AND EXTRACT(MONTH FROM pa.fecha_consumo) = numero_mes
                                                AND EXTRACT(YEAR FROM pa.fecha_consumo) = anio
                                            GROUP BY pr.nombre
                                        ) cp
                                        UNION ALL
                                        SELECT proveedor_nombre, valor_cuota, fecha_cuota as fecha_transaccion, 'Pago Cuota Consumo'::character varying as tipo_transaccion, 2 as orden FROM (
                                            SELECT pc.fecha_descuento AS fecha_cuota, pr.nombre AS proveedor_nombre, pc.valor_cuota AS valor_cuota
                                            FROM public."Pagos_pagos_cuotas" pc
                                            INNER JOIN public.proveedores_proveedor pr ON pc.proveedor_id = pr.id
                                            INNER JOIN public."Pagos_detalle_cuotas" dc ON pc.id = dc.pago_cuota_id
                                            WHERE pc.socio_id = id_socio
                                                AND EXTRACT(MONTH FROM dc.fecha_descuento) = numero_mes
                                                AND EXTRACT(YEAR FROM dc.fecha_descuento) = anio
                                        ) cu
                                        UNION ALL
                                        SELECT tipo_aportacion, montoa_aportacion, sa.fecha as fecha_transaccion, 'Aportación'::character varying as tipo_transaccion, 3 as orden FROM (
                                            SELECT tipo_aportacion, sa.monto AS montoa_aportacion, sa.fecha, 'Aportación'::character varying as tipo_transaccion
                                            FROM public.socios_aportaciones sa
                                            WHERE sa.socio_id = id_socio
                                                AND EXTRACT(MONTH FROM sa.fecha) = numero_mes
                                                AND EXTRACT(YEAR FROM sa.fecha) = anio
                                        ) sa
                                        UNION ALL
                                        SELECT 'Cuota de Préstamo'::character varying as proveedor_nombre, pp.monto_pago as valor, pp.fecha_pago as fecha_transaccion, 'Cuota de Préstamo'::character varying as tipo_transaccion, 4 as orden
                                        FROM public."Prestamos_pagomensual" pp
                                        INNER JOIN public."Prestamos_prestamo" pr ON pp.prestamo_id = pr.id
                                        WHERE pp.socio_id = id_socio
                                            AND EXTRACT(MONTH FROM pp.fecha_pago) = numero_mes
                                            AND EXTRACT(YEAR FROM pp.fecha_pago) = anio
                                            --AND pp.cancelado = false
                                        UNION ALL
                                        SELECT descripcion, valor_aportado, ae.fecha as fecha_transaccion, 'Ayuda Económica'::character varying as tipo_transaccion, 5 as orden FROM (
                                            SELECT ae.descripcion, da.valor AS valor_aportado, ae.fecha
                                            FROM public.ayudas_econ_ayudaseconomicas ae
                                            INNER JOIN public.ayudas_econ_detallesayuda da ON ae.id = da.ayuda_id
                                            WHERE da.socio_id = id_socio
                                                AND EXTRACT(MONTH FROM ae.fecha) = numero_mes
                                                AND EXTRACT(YEAR FROM ae.fecha) = anio
                                                AND EXTRACT(MONTH FROM da.fecha) = numero_mes
                                                AND EXTRACT(YEAR FROM da.fecha) = anio
                                                --AND da.cancelado = true
                                        ) ae
                                    ) AS subquery;

                                    -- Calcular la suma total desde la tabla temporal
                                    SELECT SUM(valor) INTO total FROM temp_result;

                                    -- Devolver los resultados de la subconsulta
                                    RETURN QUERY
                                    SELECT proveedor_nombre, valor, fecha_transaccion, tipo_transaccion FROM temp_result
                                    ORDER BY proveedor_nombre;

                                    -- Agregar fila "Total"
                                    RETURN QUERY
                                    SELECT 'Total'::character varying as columna1, total as columna2, null::date as columna3, null::character varying as columna4;

                                    -- Eliminar la tabla temporal al finalizar
                                    DROP TABLE IF EXISTS temp_result;
                                END;
                                
                $BODY$;

                """
            )

create_function1="""
CREATE OR REPLACE FUNCTION crear_detalles_cupo_nuevo_socio()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.proveedores_detallescupos (cupo, fechaccupo, proveedor_id, socio_id, permanente)
    SELECT p.cupo, CURRENT_DATE, p.id, NEW.id, false
    FROM public.proveedores_proveedor p;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

create_function2="""
CREATE OR REPLACE FUNCTION crear_detalles_cupo_nuevo_proveedor()
RETURNS TRIGGER AS $$
DECLARE
    socio_id bigint;
BEGIN
    FOR socio_id IN (SELECT id FROM public.socios_socios) -- Obtener todos los IDs de socios
    LOOP
        INSERT INTO public.proveedores_detallescupos (cupo, fechaccupo, proveedor_id, socio_id, permanente)
        VALUES (NEW.cupo, CURRENT_DATE, NEW.id, socio_id, false);
    END LOOP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

create_function3="""
CREATE OR REPLACE FUNCTION actualizar_detalles_cupo_cambio_cupo()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE public.proveedores_detallescupos
    SET cupo = NEW.cupo
    WHERE proveedor_id = NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

create_function4="""
CREATE OR REPLACE FUNCTION distribuir_aportacion()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.tipo_aportacion = 'AE' THEN
        -- Actualiza la tabla de total de ayuda permanente
        INSERT INTO socios_total_ayuda_permanente (tipo_aportacion, total_actual, fecha_transaccion)
        VALUES (
            'EA',
            COALESCE((SELECT total_actual FROM socios_total_ayuda_permanente WHERE tipo_aportacion = 'EA'), 0) + NEW.monto,
            NEW.fecha
        )
        ON CONFLICT (tipo_aportacion) DO UPDATE
        SET
            total_actual = EXCLUDED.total_actual,
            fecha_transaccion = EXCLUDED.fecha_transaccion;
    ELSIF NEW.tipo_aportacion = 'CO' THEN
        -- Actualiza la tabla de total de cuota ordinaria
        INSERT INTO socios_total_cuota_ordinaria (tipo_aportacion, total_actual, fecha_transaccion)
        VALUES (
            'CO',
            COALESCE((SELECT total_actual FROM socios_total_cuota_ordinaria WHERE tipo_aportacion = 'CO'), 0) + NEW.monto,
            NEW.fecha
        )
        ON CONFLICT (tipo_aportacion) DO UPDATE
        SET
            total_actual = EXCLUDED.total_actual,
            fecha_transaccion = EXCLUDED.fecha_transaccion;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

create_function5="""
CREATE OR REPLACE FUNCTION actualizar_total_y_cancelado()
RETURNS TRIGGER AS $$
BEGIN
    -- Actualizar el campo total en ayudas_econ_ayudaseconomicas
    UPDATE ayudas_econ_ayudaseconomicas AS ae
    SET total = total + NEW.valor
    WHERE ae.id = NEW.ayuda_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

create_function6="""
CREATE OR REPLACE FUNCTION actualizar_total_despues_de_insertar()
RETURNS TRIGGER AS $$
BEGIN
    DECLARE
        nuevo_valor numeric(8,2);
    BEGIN
        nuevo_valor := NEW.valor;
        
        UPDATE ayudas_econ_ayudaseconomicas
        SET total = total + nuevo_valor
        WHERE id = NEW.detalle_id;
        
        RETURN NEW;
    END;
END;
$$ LANGUAGE plpgsql;
"""

create_function7="""
CREATE OR REPLACE FUNCTION public.actualizar_cuota_ordinaria()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE NOT LEAKPROOF
AS $BODY$
BEGIN
  -- Verificar si el tipo es 'r' (Restar)
  IF NEW.tipo = 'r' THEN
    -- Restar el valor de la cuota ordinaria actual
    UPDATE socios_total_cuota_ordinaria
    SET total_actual = total_actual - NEW.valor
    WHERE tipo_aportacion = 'CO';
  -- Verificar si el tipo es 's' (Sumar)
  ELSIF NEW.tipo = 's' THEN
    -- Sumar el valor a la tabla total_ayuda_economica
    UPDATE socios_total_cuota_ordinaria
    SET total_actual = total_actual + NEW.valor
	WHERE tipo_aportacion = 'CO';
  END IF;

  RETURN NEW;
END;
$BODY$;
"""

create_function8="""
CREATE OR REPLACE FUNCTION public.sumar_valor_despues_delete()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE NOT LEAKPROOF
AS $BODY$
BEGIN
    IF OLD.socio_id IS NOT NULL AND OLD.brinda_ayuda THEN
        -- Sumar el valor a la tabla socios_total_ayuda_permanente
        UPDATE public.socios_total_ayuda_permanente
        SET total_actual = total_actual + OLD.total
        WHERE tipo_aportacion = 'EA'; -- Elige el tipo de aportación adecuado
    END IF;
    RETURN OLD;
END;
$BODY$;
"""

create_function9="""
CREATE OR REPLACE FUNCTION sumar_cuota_ordinaria()
RETURNS TRIGGER AS $$
BEGIN
  -- Suma el valor eliminado a la tabla socios_total_cuota_ordinaria
  UPDATE socios_total_cuota_ordinaria
  SET total_actual = total_actual + OLD.valor
  WHERE tipo_aportacion = 'CO';

  RETURN OLD;
END;
$$ LANGUAGE plpgsql;
"""

create_function10="""
CREATE OR REPLACE FUNCTION restar_valor_despues_insert()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.socio_id IS NULL AND NEW.brinda_ayuda THEN
        -- Restar el valor de la tabla socios_total_cuota_ordinaria
        UPDATE public.socios_total_cuota_ordinaria
        SET total_actual = total_actual - NEW.total
        WHERE tipo_aportacion = 'CO'; -- Elige el tipo de aportación adecuado
    ELSIF NEW.socio_id IS NOT NULL AND NEW.brinda_ayuda THEN
        -- Restar el valor de la tabla socios_total_ayuda_permanente
        UPDATE public.socios_total_ayuda_permanente
        SET total_actual = total_actual - NEW.total
        WHERE tipo_aportacion = 'EA'; -- Elige el tipo de aportación adecuado
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""
create_function11="""
CREATE OR REPLACE FUNCTION public.actualizar_pagosp()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE NOT LEAKPROOF
AS $BODY$
Declare comi numeric(8,2);
BEGIN
     IF TG_OP = 'INSERT' THEN
	 	comi := (SELECT comision FROM "proveedores_proveedor" WHERE id = NEW.proveedor_id);
        -- Verificar si el registro existe en proveedor_pagos
        IF EXISTS (
            SELECT 1
            FROM "PagosProveedor_pagosproveedor"
            WHERE proveedor_id = NEW.proveedor_id
        ) THEN
            -- Actualizar el valor acumulado
			IF (SELECT count(valor_cancelado) FROM "PagosProveedor_pagosproveedor" WHERE proveedor_id = NEW.proveedor_id and valor_cancelado = 'false' ) =  1 then
				UPDATE "PagosProveedor_pagosproveedor"
				SET valor_total = valor_total + NEW.consumo_total,
			    comision = ((valor_total + NEW.consumo_total) *  (comi/100))
				WHERE proveedor_id = NEW.proveedor_id;
			ELSE
				INSERT INTO "PagosProveedor_pagosproveedor"  (proveedor_id, valor_total,comision, fecha_creacion, valor_cancelado)
            	VALUES (NEW.proveedor_id,NEW.consumo_total, (NEW.consumo_total) *  (comi/100), NEW.fecha_consumo, 'false');	
			END IF;
        ELSE
            -- Insertar un nuevo registro en proveedor_pago	
			 INSERT INTO "PagosProveedor_pagosproveedor"  (proveedor_id, valor_total,comision, fecha_creacion, valor_cancelado)
            	VALUES (NEW.proveedor_id,NEW.consumo_total, (NEW.consumo_total) *  (comi/100), NEW.fecha_consumo, 'false');
        END IF;
    ELSIF TG_OP = 'DELETE' THEN
		comi := (SELECT comision FROM "proveedores_proveedor" WHERE id = OLD.proveedor_id);
        -- Actualizar el valor acumulado y la comisión al eliminar pagos
        UPDATE "PagosProveedor_pagosproveedor"
        SET valor_total = valor_total - OLD.consumo_total,
            comision = ((valor_total - OLD.consumo_total) * (comi/100))
        WHERE proveedor_id = OLD.proveedor_id;		
    END IF;
    RETURN NEW;
END;
$BODY$;
"""

create_trigger1="""
CREATE TRIGGER trigger_nuevo_socio
AFTER INSERT ON public.socios_socios
FOR EACH ROW
EXECUTE FUNCTION crear_detalles_cupo_nuevo_socio();
"""

create_trigger2="""
CREATE TRIGGER trigger_nuevo_proveedor
AFTER INSERT ON public.proveedores_proveedor
FOR EACH ROW
EXECUTE FUNCTION crear_detalles_cupo_nuevo_proveedor();
"""

create_trigger3="""
CREATE TRIGGER trigger_cambio_cupo
AFTER UPDATE OF cupo ON public.proveedores_proveedor
FOR EACH ROW
EXECUTE FUNCTION actualizar_detalles_cupo_cambio_cupo();
"""

create_trigger4="""
CREATE TRIGGER distribuir_aportacion_trigger
AFTER INSERT ON socios_aportaciones
FOR EACH ROW
EXECUTE FUNCTION distribuir_aportacion();
"""

create_trigger5="""
CREATE TRIGGER actualizar_total_y_cancelado_trigger
AFTER UPDATE ON ayudas_econ_detallesayuda
FOR EACH ROW
WHEN (OLD.valor IS DISTINCT FROM NEW.valor)
EXECUTE FUNCTION actualizar_total_y_cancelado();
"""

create_trigger6="""
CREATE TRIGGER actualizar_total_despues_de_insertar_trigger
AFTER INSERT ON ayudas_econ_ayudasexternas
FOR EACH ROW
EXECUTE FUNCTION actualizar_total_despues_de_insertar();
"""

create_trigger7="""
CREATE TRIGGER trigger_restar_cuota_ordinaria
AFTER INSERT ON ayudas_econ_consumoscuotaordinaria
FOR EACH ROW
EXECUTE FUNCTION actualizar_cuota_ordinaria();
"""

create_trigger8="""
CREATE TRIGGER sumar_valor_trigger_delete
AFTER DELETE ON public.ayudas_econ_ayudaseconomicas
FOR EACH ROW
EXECUTE FUNCTION sumar_valor_despues_delete();
"""

create_trigger9="""
CREATE TRIGGER sumar_valor_cuota_ordinaria
BEFORE DELETE ON ayudas_econ_consumoscuotaordinaria
FOR EACH ROW
EXECUTE FUNCTION sumar_cuota_ordinaria();
"""

create_trigger10="""
CREATE TRIGGER restar_valor_trigger
AFTER INSERT ON public.ayudas_econ_ayudaseconomicas
FOR EACH ROW
EXECUTE FUNCTION restar_valor_despues_insert();
"""
create_trigger11="""
CREATE OR REPLACE TRIGGER trigger_actualizar_pagosp
    AFTER INSERT OR DELETE
    ON public."Pagos_pagos"
    FOR EACH ROW
    EXECUTE FUNCTION public.actualizar_pagosp();
"""


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
        migrations.RunPython(actualizar_descuentos),
        migrations.RunPython(actualizar_estados),
        migrations.RunPython(actualizar_estados_ayudas),
        migrations.RunPython(actualizar_estados_ayudas_exter),
        migrations.RunPython(obtener_aportaciones_externas_func),
        migrations.RunPython(obtener_suma_aportaciones_externas_func),
        migrations.RunPython(obtener_suma_aportaciones_func),
        migrations.RunPython(obtener_ayudas_func), 
        migrations.RunPython(obtener_consumo_total_func),
        migrations.RunPython(obtener_consumo_total_todos_func),
        migrations.RunPython(obtener_consumos_proveedores_func),
        migrations.RunPython(obtener_consumos_por_proveedor_detalle_cuotas),
        migrations.RunPython(obtener_cuota_descuentos_total_func),
        migrations.RunPython(obtener_cuota_descuentos_func),
        migrations.RunPython(obtener_cuota_prestamos_func),
        migrations.RunPython(obtener_suma_ayudas_func),
        migrations.RunPython(obtener_suma_consumo_total_descuentos_func),
        migrations.RunPython(obtener_suma_descuento_cuotas_func),
        migrations.RunPython(obtener_suma_prestamo_total_func),
        migrations.RunPython(obtener_suma_total),
        migrations.RunPython(total_des_pen),
        migrations.RunPython(obtener_informe_mensual2),
        migrations.RunSQL(create_function1),
        migrations.RunSQL(create_function2),
        migrations.RunSQL(create_function3),
        migrations.RunSQL(create_function4),
        migrations.RunSQL(create_function5),
        migrations.RunSQL(create_function6),
        migrations.RunSQL(create_function7),
        migrations.RunSQL(create_function8),
        migrations.RunSQL(create_function9),
        migrations.RunSQL(create_function10),
        migrations.RunSQL(create_function11),
        migrations.RunSQL(create_trigger1),
        migrations.RunSQL(create_trigger2),
        migrations.RunSQL(create_trigger3),
        migrations.RunSQL(create_trigger4),
        migrations.RunSQL(create_trigger5),
        migrations.RunSQL(create_trigger6),
        migrations.RunSQL(create_trigger7),
        migrations.RunSQL(create_trigger8),
        migrations.RunSQL(create_trigger9),
        migrations.RunSQL(create_trigger10),
        migrations.RunSQL(create_trigger11),
    ]
