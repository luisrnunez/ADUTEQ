from django.db import migrations

CREATE_FUNCTION = """
CREATE OR REPLACE FUNCTION public.obtener_total_comisiones(
	mes integer,
	anio integer)
    RETURNS numeric
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE
    total_comision NUMERIC(8, 2);
BEGIN
    SELECT SUM(p.consumo_total * pp.comision / 100)
    INTO total_comision
    FROM "Pagos_pagos" p
    JOIN proveedores_proveedor pp ON p.proveedor_id = pp.id
    WHERE EXTRACT(MONTH FROM p.fecha_consumo) = mes
    AND EXTRACT(YEAR FROM p.fecha_consumo) = anio
	and p.estado= True;

    IF total_comision IS NULL THEN
        total_comision := 0;
    END IF;

    RETURN total_comision;
END;
$BODY$;
"""

CREATE_FUNCTION2 = """
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

CREATE_FUNCTION3 = """
CREATE OR REPLACE FUNCTION public.obtener_suma_descuento_cuotas_pagados_func(
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
                                    and estado=True;

                                    RETURN total_pago;
                                END;
                                
                
$BODY$;
"""

CREATE_FUNCTION4 = """
CREATE OR REPLACE FUNCTION public.obtener_suma_consumo_total_descuentos_pagados_func(
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
                                    and estado = True;

                                    RETURN suma_consumo;
                                END;
                                
                
$BODY$;
"""

CREATE_FUNCTION5 = """
CREATE OR REPLACE FUNCTION public.obtener_total_comisiones_desc(
	mes integer,
	anio integer)
    RETURNS numeric
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE
    total_comision NUMERIC(8, 2);
BEGIN
    SELECT SUM(pd.valor_cuota * pp.comision / 100)
    INTO total_comision
    FROM "Pagos_detalle_cuotas" pd
    JOIN proveedores_proveedor pp ON pd.proveedor_id = pp.id
    WHERE EXTRACT(MONTH FROM pd.fecha_descuento) = mes
    AND EXTRACT(YEAR FROM pd.fecha_descuento) = anio
	and pd.estado = True;

    IF total_comision IS NULL THEN
        total_comision := 0;
    END IF;

    RETURN total_comision;
END;
$BODY$;
"""

CREATE_FUNCTION6 = """
CREATE OR REPLACE FUNCTION public.obtener_suma_intereses_prestamos(
	mes integer,
	anio integer)
    RETURNS numeric
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$
DECLARE
    total_intereses NUMERIC(10, 2);
BEGIN
    SELECT SUM(pm.monto_pago - (pm.monto_pago / (1 + (p.tasa_interes / 100))))
    INTO total_intereses
    FROM "Prestamos_pagomensual" pm
    JOIN "Prestamos_prestamo" p ON pm.prestamo_id = p.id
    WHERE EXTRACT(MONTH FROM pm.fecha_pago) = mes
    AND EXTRACT(YEAR FROM pm.fecha_pago) = anio
	and pm.cancelado=True;

    IF total_intereses IS NULL THEN
        total_intereses := 0;
    END IF;

    RETURN total_intereses;
END;
$BODY$;
"""

CREATE_FUNCTION7 = """
CREATE OR REPLACE FUNCTION public.obtener_informacion_prestamos(
	mes integer,
	anio integer)
    RETURNS TABLE(nombres text, valor_cuota numeric, valor_cuota_interes numeric) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
BEGIN
    RETURN QUERY
    SELECT
        CONCAT(u.last_name, ' ', u.first_name) AS Nombres,
		pm.monto_pago / (1 + (p.tasa_interes / 100)) AS valor_cuota_original,
        pm.monto_pago AS valor_cuota
    FROM
        "Prestamos_pagomensual" pm
    JOIN
        "Prestamos_prestamo" p ON pm.prestamo_id = p.id
    JOIN
        socios_socios s ON p.socio_id = s.id
    JOIN
        auth_user u ON s.user_id = u.id
    WHERE
        EXTRACT(MONTH FROM pm.fecha_pago) = mes
        AND EXTRACT(YEAR FROM pm.fecha_pago) = anio
		and pm.cancelado=true;

END;
$BODY$;
"""

CREATE_FUNCTION8 = """
CREATE OR REPLACE FUNCTION public.obtener_comision_descuentos(
	mes integer,
	anio integer)
    RETURNS TABLE(nombre_proveedor character varying, consumo_total numeric, valor_comision numeric) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
BEGIN
    RETURN QUERY
    SELECT
        pp.nombre AS nombre_proveedor,
        SUM(p.consumo_total) AS consumo_total,
        SUM(p.consumo_total * pp.comision / 100) AS valor_comision
    FROM
        "Pagos_pagos" p
    JOIN
        proveedores_proveedor pp ON p.proveedor_id = pp.id
    WHERE
        EXTRACT(MONTH FROM p.fecha_consumo) = mes
        AND EXTRACT(YEAR FROM p.fecha_consumo) = anio
		and p.estado=True
    GROUP BY
        pp.nombre
    ORDER BY
        pp.nombre;

END;
$BODY$;
"""

CREATE_FUNCTION9 = """
CREATE OR REPLACE FUNCTION public.obtener_comision_descuentos_cuotas(
	mes integer,
	anio integer)
    RETURNS TABLE(nombre_proveedor character varying, consumo_total numeric, valor_comision numeric) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
BEGIN
    RETURN QUERY
    SELECT
        pp.nombre AS nombre_proveedor,
        SUM(pd.valor_cuota) AS consumo_total,
        SUM(pd.valor_cuota * pp.comision / 100) AS valor_comision
    FROM
        "Pagos_detalle_cuotas" pd
    JOIN
        proveedores_proveedor pp ON pd.proveedor_id = pp.id
    WHERE
        EXTRACT(MONTH FROM pd.fecha_descuento) = mes
        AND EXTRACT(YEAR FROM pd.fecha_descuento) = anio
		and pd.estado=True
    GROUP BY
        pp.nombre
    ORDER BY
        pp.nombre;

END;
$BODY$;
"""

CREATE_FUNCTION10 = """

CREATE OR REPLACE PROCEDURE public.obtener_consumo_proveedores(
	IN mes integer,
	IN anio integer)
LANGUAGE 'plpgsql'
AS $BODY$
DECLARE
    columnas_proveedores text;
    sqlt text;
    proveedor_nombre text;
BEGIN
    -- Obtener los nombres de proveedores únicos como filas
    CREATE TEMP TABLE proveedores_temp AS
        SELECT DISTINCT nombre
        FROM public.proveedores_proveedor
        ORDER BY nombre;

    -- Construir la lista de nombres de proveedores como columnas en la consulta dinámica
    columnas_proveedores := '';
    FOR proveedor_nombre IN (SELECT nombre FROM proveedores_temp)
    LOOP
        columnas_proveedores := columnas_proveedores || ',' || quote_ident(REPLACE(proveedor_nombre, ' ', '_')) || ' numeric';
    END LOOP;
    columnas_proveedores := substring(columnas_proveedores FROM 2);

    -- Eliminar la tabla temporal de consumo_proveedores si ya existe
    DROP TABLE IF EXISTS consumo_proveedores;

    -- Construir la consulta dinámicamente con los parámetros mes y anio
    sqlt := '
        CREATE TEMP TABLE consumo_proveedores AS
        SELECT *
        FROM crosstab(
            ''SELECT s.cedula AS cedula, u.first_name as nombres, u.last_name as apellidos, pr.nombre AS nombre_proveedor, SUM(p.consumo_total) AS total_consumido
            FROM public."Pagos_pagos" p
            INNER JOIN public.socios_socios s ON p.socio_id = s.id
			INNER JOIN public.auth_user u ON s.user_id = u.id
            INNER JOIN public.proveedores_proveedor pr ON p.proveedor_id = pr.id
            WHERE EXTRACT(MONTH FROM p.fecha_consumo) = ' || mes || ' AND EXTRACT(YEAR FROM p.fecha_consumo) = ' || anio || '
            GROUP BY s.cedula, u.first_name, u.last_name, pr.nombre
            ORDER BY apellidos, nombres, pr.nombre'',
            ''SELECT DISTINCT nombre FROM proveedores_temp ORDER BY 1''
        ) AS ct (
            cedula text,
			nombres text,
			apellidos text,
            ' || columnas_proveedores || '
        )
    ';

    -- Ejecutar la consulta dinámicamente
    EXECUTE sqlt;

    -- Eliminar la tabla temporal de proveedores_temp
    DROP TABLE IF EXISTS proveedores_temp;
END;
$BODY$;
"""

class Migration(migrations.Migration):

    dependencies = [
        ('Pagos', '0001_initial'),
        ('PagosProveedor', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(CREATE_FUNCTION),
        migrations.RunSQL(CREATE_FUNCTION2),
        migrations.RunSQL(CREATE_FUNCTION3),
        migrations.RunSQL(CREATE_FUNCTION4),
        migrations.RunSQL(CREATE_FUNCTION5),
        migrations.RunSQL(CREATE_FUNCTION6),
        migrations.RunSQL(CREATE_FUNCTION7),
        migrations.RunSQL(CREATE_FUNCTION8),
        migrations.RunSQL(CREATE_FUNCTION9),
        migrations.RunSQL(CREATE_FUNCTION10),
    ]
