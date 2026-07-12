from django.db import migrations


def create_superuser(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Profile = apps.get_model('main', 'Profile')
    if not User.objects.filter(username='admin').exists():
        user = User.objects.create_superuser(
            username='admin',
            email='admin@megano.ru',
            password='admin123',
        )
        Profile.objects.create(user=user, full_name='Administrator')


def remove_superuser(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User.objects.filter(username='admin').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_order_deleted_at_order_is_deleted_profile_deleted_at_and_more'),
    ]

    operations = [
        migrations.RunPython(create_superuser, remove_superuser),
    ]
