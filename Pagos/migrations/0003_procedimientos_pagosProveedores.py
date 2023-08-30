from django.db import migrations

CREATE_FUNCTION = """
CREATE OR REPLACE FUNCTION actualizar_pagosp()
RETURNS TRIGGER AS $$
BEGIN
     IF TG_OP = 'INSERT' THEN
        -- Verificar si el registro existe en proveedor_pagos
        IF EXISTS (
            SELECT 1
            FROM "PagosProveedor_pagosproveedor"
            WHERE proveedor_id = NEW.proveedor_id
        ) THEN
            -- Actualizar el valor acumulado
			IF (SELECT count(valor_cancelado) FROM "PagosProveedor_pagosproveedor" WHERE proveedor_id = NEW.proveedor_id and valor_cancelado = 'false') =  1 then
				UPDATE "PagosProveedor_pagosproveedor"
				SET valor_total = valor_total + NEW.consumo_total
				WHERE proveedor_id = NEW.proveedor_id;
			ELSE
				INSERT INTO "PagosProveedor_pagosproveedor"  (proveedor_id, valor_total, fecha_creacion, valor_cancelado)
            	VALUES (NEW.proveedor_id, NEW.consumo_total, current_date, 'false');	
			END IF;
        ELSE
            -- Insertar un nuevo registro en proveedor_pago	
			 INSERT INTO "PagosProveedor_pagosproveedor"  (proveedor_id, valor_total, fecha_creacion, valor_cancelado)
            VALUES (NEW.proveedor_id, NEW.consumo_total, current_date, 'false');
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

CREATE_TRIGGER = """
CREATE TRIGGER trigger_actualizar_pagosp
AFTER INSERT ON "Pagos_pagos"
FOR EACH ROW
EXECUTE FUNCTION actualizar_pagosp();
"""

CREATE_TRIGGER2 = """
CREATE TRIGGER trigger_actualizar_pagosc
AFTER INSERT ON "Pagos_pagos_cuotas"
FOR EACH ROW
EXECUTE FUNCTION actualizar_pagosp();
"""

class Migration(migrations.Migration):

    dependencies = [
        ('Pagos', '0001_initial'),
        ('PagosProveedor', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(CREATE_FUNCTION),
        migrations.RunSQL(CREATE_TRIGGER),
        migrations.RunSQL(CREATE_TRIGGER2),
    ]
