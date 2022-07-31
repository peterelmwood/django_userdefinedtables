# Generated by Django 4.0.5 on 2022-07-30 19:03

import datetime
from django.db import migrations, models
import django.db.models.constraints
import django.db.models.deletion
import django.db.models.expressions


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choice', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Column',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('required', models.BooleanField(default=False)),
                ('unique', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='List',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='BinaryColumn',
            fields=[
                ('column_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='userdefinedtables.column')),
            ],
            bases=('userdefinedtables.column',),
        ),
        migrations.CreateModel(
            name='BinaryColumnEntry',
            fields=[
                ('entry_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='userdefinedtables.entry')),
                ('value', models.BooleanField()),
            ],
            bases=('userdefinedtables.entry',),
        ),
        migrations.CreateModel(
            name='ChoiceColumn',
            fields=[
                ('column_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='userdefinedtables.column')),
            ],
            bases=('userdefinedtables.column',),
        ),
        migrations.CreateModel(
            name='ChoiceEntry',
            fields=[
                ('entry_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='userdefinedtables.entry')),
            ],
            bases=('userdefinedtables.entry',),
        ),
        migrations.CreateModel(
            name='CurrencyColumn',
            fields=[
                ('column_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='userdefinedtables.column')),
                ('minimum', models.DecimalField(decimal_places=4, default=None, max_digits=16, null=True)),
                ('maximum', models.DecimalField(decimal_places=4, default=None, max_digits=16, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('userdefinedtables.column', models.Model),
        ),
        migrations.CreateModel(
            name='CurrencyEntry',
            fields=[
                ('entry_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='userdefinedtables.entry')),
                ('value', models.DecimalField(decimal_places=4, max_digits=16)),
            ],
            bases=('userdefinedtables.entry',),
        ),
        migrations.CreateModel(
            name='DateTimeColumn',
            fields=[
                ('column_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='userdefinedtables.column')),
                ('earliest_date', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0), null=True)),
                ('latest_date', models.DateTimeField(default=None, null=True)),
            ],
            bases=('userdefinedtables.column',),
        ),
        migrations.CreateModel(
            name='DateTimeColumnEntry',
            fields=[
                ('entry_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='userdefinedtables.entry')),
                ('value', models.DateTimeField()),
            ],
            bases=('userdefinedtables.entry',),
        ),
        migrations.CreateModel(
            name='LookupColumn',
            fields=[
                ('column_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='userdefinedtables.column')),
            ],
            bases=('userdefinedtables.column',),
        ),
        migrations.CreateModel(
            name='LookupColumnEntry',
            fields=[
                ('entry_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='userdefinedtables.entry')),
            ],
            bases=('userdefinedtables.entry',),
        ),
        migrations.CreateModel(
            name='MultipleLineTextColumn',
            fields=[
                ('column_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='userdefinedtables.column')),
            ],
            bases=('userdefinedtables.column',),
        ),
        migrations.CreateModel(
            name='MultipleLineTextColumnEntry',
            fields=[
                ('entry_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='userdefinedtables.entry')),
                ('value', models.TextField(blank=True)),
            ],
            bases=('userdefinedtables.entry',),
        ),
        migrations.CreateModel(
            name='NumberColumn',
            fields=[
                ('column_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='userdefinedtables.column')),
                ('minimum', models.DecimalField(decimal_places=4, default=None, max_digits=16, null=True)),
                ('maximum', models.DecimalField(decimal_places=4, default=None, max_digits=16, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('userdefinedtables.column', models.Model),
        ),
        migrations.CreateModel(
            name='NumberEntry',
            fields=[
                ('entry_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='userdefinedtables.entry')),
                ('value', models.DecimalField(decimal_places=4, max_digits=16)),
            ],
            bases=('userdefinedtables.entry',),
        ),
        migrations.CreateModel(
            name='PictureColumn',
            fields=[
                ('column_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='userdefinedtables.column')),
            ],
            bases=('userdefinedtables.column',),
        ),
        migrations.CreateModel(
            name='PictureColumnEntry',
            fields=[
                ('entry_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='userdefinedtables.entry')),
                ('value', models.ImageField(upload_to='')),
            ],
            bases=('userdefinedtables.entry',),
        ),
        migrations.CreateModel(
            name='SingleLineOfTextColumn',
            fields=[
                ('column_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='userdefinedtables.column')),
                ('maximum_length', models.PositiveSmallIntegerField(default=255)),
            ],
            bases=('userdefinedtables.column',),
        ),
        migrations.CreateModel(
            name='URLColumn',
            fields=[
                ('column_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='userdefinedtables.column')),
            ],
            bases=('userdefinedtables.column',),
        ),
        migrations.CreateModel(
            name='Row',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.PositiveBigIntegerField()),
                ('list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rows', to='userdefinedtables.list')),
            ],
        ),
        migrations.AddField(
            model_name='entry',
            name='row',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='row_entries', to='userdefinedtables.row'),
        ),
        migrations.AddField(
            model_name='column',
            name='list',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='columns', to='userdefinedtables.list'),
        ),
        migrations.CreateModel(
            name='URLColumnEntry',
            fields=[
                ('entry_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='userdefinedtables.entry')),
                ('value', models.URLField()),
                ('column', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='userdefinedtables.urlcolumn')),
            ],
            bases=('userdefinedtables.entry',),
        ),
        migrations.CreateModel(
            name='SingleLineOfTextColumnEntry',
            fields=[
                ('entry_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='userdefinedtables.entry')),
                ('value', models.CharField(blank=True, max_length=255)),
                ('column', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='userdefinedtables.singlelineoftextcolumn')),
            ],
            bases=('userdefinedtables.entry',),
        ),
        migrations.AddConstraint(
            model_name='singlelineoftextcolumn',
            constraint=models.CheckConstraint(check=models.Q(('maximum_length__lte', 255)), name='maximum_length cannot exceed 255'),
        ),
        migrations.AddConstraint(
            model_name='row',
            constraint=models.UniqueConstraint(deferrable=django.db.models.constraints.Deferrable['DEFERRED'], fields=('list', 'index'), name='A list can only have a single row at an index.'),
        ),
        migrations.AddField(
            model_name='picturecolumnentry',
            name='column',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='userdefinedtables.picturecolumn'),
        ),
        migrations.AddField(
            model_name='numberentry',
            name='column',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='userdefinedtables.numbercolumn'),
        ),
        migrations.AddConstraint(
            model_name='numbercolumn',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('maximum__gte', django.db.models.expressions.F('minimum')), ('maximum__isnull', False), ('minimum__isnull', False)), ('maximum__isnull', True), ('minimum__isnull', True), _connector='OR'), name='numbercolumn.minimum cannot exceed numbercolumn.maximum.'),
        ),
        migrations.AddField(
            model_name='multiplelinetextcolumnentry',
            name='column',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='userdefinedtables.multiplelinetextcolumn'),
        ),
        migrations.AddField(
            model_name='lookupcolumnentry',
            name='column',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='userdefinedtables.lookupcolumn'),
        ),
        migrations.AddField(
            model_name='lookupcolumnentry',
            name='value',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='lookup_selections', to='userdefinedtables.entry'),
        ),
        migrations.AddField(
            model_name='lookupcolumn',
            name='lookup_column',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lookup_columns', to='userdefinedtables.column'),
        ),
        migrations.AddField(
            model_name='lookupcolumn',
            name='lookup_list',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lookups', to='userdefinedtables.list'),
        ),
        migrations.AddField(
            model_name='datetimecolumnentry',
            name='column',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='userdefinedtables.datetimecolumn'),
        ),
        migrations.AddField(
            model_name='currencyentry',
            name='column',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='userdefinedtables.currencycolumn'),
        ),
        migrations.AddConstraint(
            model_name='currencycolumn',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('maximum__gte', django.db.models.expressions.F('minimum')), ('maximum__isnull', False), ('minimum__isnull', False)), ('maximum__isnull', True), ('minimum__isnull', True), _connector='OR'), name='currencycolumn.minimum cannot exceed currencycolumn.maximum.'),
        ),
        migrations.AddConstraint(
            model_name='column',
            constraint=models.UniqueConstraint(fields=('name', 'list'), name='Column name cannot occur twice in one list'),
        ),
        migrations.AddField(
            model_name='choiceentry',
            name='column',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='userdefinedtables.choicecolumn'),
        ),
        migrations.AddField(
            model_name='choiceentry',
            name='value',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='choices', to='userdefinedtables.choice'),
        ),
        migrations.AddField(
            model_name='binarycolumnentry',
            name='column',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='userdefinedtables.binarycolumn'),
        ),
    ]
