# Generated by Django 4.2.10 on 2024-02-14 13:17

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import ratemymodule.models.managers
import ratemymodule.models.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('date_time_created', models.DateTimeField(auto_now_add=True, verbose_name='Date & Time Created')),
                ('email', models.EmailField(error_messages={'max_length': 'The Email Address must be at most 255 digits.', 'unique': 'A user with that Email Address already exists.'}, max_length=255, unique=True, validators=[ratemymodule.models.validators.HTML5EmailValidator(), ratemymodule.models.validators.FreeEmailValidator(), ratemymodule.models.validators.ConfusableEmailValidator(), ratemymodule.models.validators.PreexistingEmailTLDValidator(), ratemymodule.models.validators.ExampleEmailValidator()], verbose_name='Email Address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into the admin site.', verbose_name='Is Admin?')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='Is Active?')),
            ],
            options={
                'verbose_name': 'User',
            },
            managers=[
                ('objects', ratemymodule.models.managers.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='OtherTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time_created', models.DateTimeField(auto_now_add=True, verbose_name='Date & Time Created')),
                ('name', models.CharField(max_length=60, unique=True, validators=[django.core.validators.MinLengthValidator(2)], verbose_name='Tag Name')),
                ('is_verified', models.BooleanField(default=False, verbose_name='Is Verified?')),
            ],
            options={
                'verbose_name': 'Other Tag',
            },
        ),
        migrations.CreateModel(
            name='ToolTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time_created', models.DateTimeField(auto_now_add=True, verbose_name='Date & Time Created')),
                ('name', models.CharField(max_length=60, unique=True, validators=[django.core.validators.MinLengthValidator(2)], verbose_name='Tag Name')),
                ('is_verified', models.BooleanField(default=False, verbose_name='Is Verified?')),
            ],
            options={
                'verbose_name': 'Tool Tag',
            },
        ),
        migrations.CreateModel(
            name='TopicTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time_created', models.DateTimeField(auto_now_add=True, verbose_name='Date & Time Created')),
                ('name', models.CharField(max_length=60, unique=True, validators=[django.core.validators.MinLengthValidator(2)], verbose_name='Tag Name')),
                ('is_verified', models.BooleanField(default=False, verbose_name='Is Verified?')),
            ],
            options={
                'verbose_name': 'Topic Tag',
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time_created', models.DateTimeField(auto_now_add=True, verbose_name='Date & Time Created')),
                ('overall_rating', models.IntegerField(choices=[(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], verbose_name='Overall Rating')),
                ('difficulty_rating', models.IntegerField(choices=[(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], verbose_name='Difficulty Rating')),
                ('assessment_rating', models.IntegerField(choices=[(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], verbose_name='Assessment Rating')),
                ('teaching_rating', models.IntegerField(choices=[(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], verbose_name='Teaching Rating')),
                ('content', models.TextField(verbose_name='Content')),
                ('academic_year_start', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1000), django.core.validators.MaxValueValidator(3000)], verbose_name='Academic Year Start')),
                ('hidden', models.BooleanField(default=False, verbose_name='Is Hidden?')),
                ('other_tag_set', models.ManyToManyField(blank=True, related_name='post_set', to='ratemymodule.othertag', verbose_name='Other Tags')),
                ('tool_tag_set', models.ManyToManyField(blank=True, related_name='post_set', to='ratemymodule.tooltag', verbose_name='Tool Tags')),
                ('topic_tag_set', models.ManyToManyField(blank=True, related_name='post_set', to='ratemymodule.topictag', verbose_name='Topic Tags')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='made_post_set', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Post',
            },
        ),
        migrations.AddField(
            model_name='user',
            name='disliked_post_set',
            field=models.ManyToManyField(blank=True, help_text='The set of posts this user has disliked.', related_name='disliked_by_users', to='ratemymodule.post', verbose_name='Disliked Posts'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='liked_post_set',
            field=models.ManyToManyField(blank=True, help_text='The set of posts this user has liked.', related_name='liked_by_users', to='ratemymodule.post', verbose_name='Liked Posts'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
    ]
