from django.db import migrations

CREATE_FUNCTION = """
CREATE OR REPLACE FUNCTION actualizar_pagosp()
RETURNS TRIGGER AS $$
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
$$ LANGUAGE plpgsql;
"""

CREATE_TRIGGER = """
CREATE TRIGGER trigger_actualizar_pagosp
AFTER INSERT OR DELETE ON "Pagos_pagos"
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
