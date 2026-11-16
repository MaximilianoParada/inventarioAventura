from django.db import migrations


def create_default_roles(apps, schema_editor):
    Role = apps.get_model('cuentas', 'Role')
    roles = [
        ('Administrador', 2, 0, 0, 0, 0),
        ('Guía / Operador', 0, 2, 2, 0, 0),
        ('Turista / Cliente', 0, 0, 0, 2, 2),
    ]

    for role_name, administrator, guide, operator, tourist, client in roles:
        Role.objects.using(schema_editor.connection.alias).update_or_create(
            role_name=role_name,
            defaults={
                'administrador': administrator,
                'guia': guide,
                'operador': operator,
                'turista': tourist,
                'cliente': client,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ('cuentas', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_roles, migrations.RunPython.noop),
    ]
