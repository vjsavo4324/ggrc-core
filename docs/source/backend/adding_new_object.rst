Adding a new Object
===================

Backend
-------

Create ``new_object.py`` in ``src/<module>/models/``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  code-block:: python

    class NewObject(mixins..., db.Model):
      __tablename__ = 'new_objects'

      new_object_attr = deferred(db.Column(db.String), 'NewObject')

      # REST properties
      _publish_attrs = [
          'new_object_attr',
      ]

Add the NewObject to the ``all_models`` list in ``all_models.py``, or
register it using the ``register_model`` method if your adding it inside
a module.

Generate a migration file
~~~~~~~~~~~~~~~~~~~~~~~~~

..  code-block:: bash

    python src/ggrc/migrate.py <module> revision --autogenerate -m "Add NewObject"

Consider the generated migration file a template that you need to
manually update.

**Important:** Make sure both ``db_migrate`` and ``db_downgrade`` are
working correctly, both in a clean database and in a database with
existing data

Add new Object to appropriate services
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. ``ggrc/cache/cache.py`` configure memcache
2. ``ggrc/services/__init__.py`` or use ``init_extra_services()`` to
   init REST APIs for NewObject
3. ``ggrc/views/__init__.py`` or use ``init_extra_views()`` to init
   object view page

Add permissions for NewObject
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add the NewObject to appropriate roles in
``ggrc_basic_permissions/roles``

Frontend
--------

Create a Cacheable object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

..  code-block:: javascript

    import Stub from '../stub';
    import Cacheable from '../cacheable';

    export default Cacheable.extend({
      root_object : "new_object",
      root_collection : "new_objects",
      findOne : "GET /api/new_objects/{id}",
      update : "PUT /api/new_objects/{id}",
      destroy : "DELETE /api/new_objects/{id}",
      create : "POST /api/new_objects",
      mixins : ["ownable", "contactable"],
      is_custom_attributable: true,
      attributes : {
        modified_by : Stub,
        custom_attribute_values : Stub.List,
        start_date: "date",
        end_date: "date"
      },
      init : function() {
        this._super && this._super.apply(this, arguments);
        this.validateNonBlank("title");
      }
    }, {

    });

1. Add ``new_object`` to ``objectTypeDecisionTree`` in
   plugins/utils/model-utils.js.
2. Add ``new_object`` to ``base_widgets.js``

   ``baseWidgetsByType`` is where you define the child widgets for new object
   
3. Add ``new_object`` to ``business_objects.js``

  ``extraDescriptorOptions`` is where you define special
   parameters for some of the widgets ie. their content controller,
   icon, widget name etc.

3. Add ``new_object`` to ``mappings-ggrc.js``

   Add the object to the list of mappings:
   ``Mappings({NewObject: {...}}``.

Extending
~~~~~~~~~

Create a ModuleExtension object:

..  code-block:: javascript

    var ModuleExtension = {
      name: "module",
      init_widgets: function() {

      },
      init_admin_widgets: function() {

      },
    }
    widgetModules.push(ModuleExtension);

Add NewObject to the LHN
~~~~~~~~~~~~~~~~~~~~~~~~

In :src:`ggrc-client/js/templates/dashboard/lhn.stache` add the line:

..  code-block:: javascript

    {{{renderLive 'dashboard/lhn_search' type="NewObject" li_class="class"}}}

Create template files
---------------------

``new_object/modal_content.stache`` is the only mandatory template
file that needs to be created. Creating all the other template files is
optional. If the template file is not found in ``new_object`` it will be
taken from ``base_objects``.
