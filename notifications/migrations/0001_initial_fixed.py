from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(choices=[('success', 'success'), ('info', 'info'), ('warning', 'warning'), ('error', 'error')], default='info', max_length=20)),
                ('recipient', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='notifications', to='auth.user')),
                ('unread', models.BooleanField(default=True)),
                ('actor_object_id', models.CharField(max_length=255)),
                ('verb', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('target_object_id', models.CharField(blank=True, max_length=255, null=True)),
                ('action_object_object_id', models.CharField(blank=True, max_length=255, null=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('public', models.BooleanField(default=True)),
                ('deleted', models.BooleanField(default=False)),
                ('emailed', models.BooleanField(default=False)),
                ('data', models.JSONField(blank=True, null=True)),
                ('actor_content_type', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='notify_actor', to='contenttypes.contenttype')),
                ('action_object_content_type', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name='notify_action_object', to='contenttypes.contenttype')),
                ('target_content_type', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name='notify_target', to='contenttypes.contenttype')),
            ],
            options={
                'ordering': ('-timestamp',),
                'abstract': False,
                'index_together': {('recipient', 'unread')},
            },
        ),
    ]
