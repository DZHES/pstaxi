# Generated by Django 4.0 on 2022-02-24 09:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('motorpool', '0012_auto_logo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='auto',
            name='logo',
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='motorpool.brand')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='auth.user')),
            ],
        ),
    ]
