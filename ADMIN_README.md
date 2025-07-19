# KatoMart Admin Interface

A modern, Material Design-based Django admin interface for the KatoMart platform.

## Features

### 🎨 Modern Material Design
- Clean, professional interface with Material Design principles
- Responsive design that works on desktop, tablet, and mobile
- Custom color scheme with CSS variables for easy theming
- Smooth animations and hover effects

### 📊 Enhanced Dashboard
- Quick action buttons for common tasks
- System status indicators
- Card-based layout for better organization
- Recent actions sidebar

### 📋 Improved Data Management
- Organized fieldsets for better data entry
- Inline editing capabilities
- Advanced filtering and search
- Bulk operations support
- Export functionality

### 🌍 Internationalization (i18n)
- Multi-language support with 10 languages configured
- Translation files for easy localization
- RTL language support ready
- Locale-specific formatting

### 🔧 Custom Admin Classes
All models have custom admin classes with:
- Optimized list displays
- Relevant filters and search fields
- Logical fieldset organization
- Read-only fields for computed values
- Custom permissions where needed

## Models and Admin Classes

### System Configuration
- **Model**: `SystemConfig`
- **Features**: Single instance management, tool path configuration
- **Fieldsets**: General Settings, Tool Paths

### Platform Management
- **Model**: `Platform`
- **Features**: Platform configuration, issue tracking
- **Fieldsets**: Basic Information, Configuration, Issues, Additional Data

### Platform URLs
- **Model**: `PlatformURL`
- **Features**: URL management, visitation limits, headers
- **Fieldsets**: Basic Information, String Formatting, Headers & Requests, Visitation Limits

### Authentication
- **Model**: `PlatformAuth`
- **Features**: Encrypted credential storage, token management
- **Fieldsets**: Authentication, Encrypted Data, Token Information

### Content Management
- **Models**: `Course`, `Module`, `Lesson`, `File`
- **Features**: Hierarchical content organization, download tracking
- **Fieldsets**: Basic Information, Identifiers, Status, Download Information, DRM

### User Management
- **Models**: `UserFormattedName`, `UserConfig`
- **Features**: User preferences, custom naming
- **Fieldsets**: User-specific configurations

## Installation

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

4. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

5. **Access Admin Interface**
   Visit: http://127.0.0.1:8000/admin/

## Configuration

### Settings
The admin interface is configured in `katomart/settings.py`:

```python
# Material Admin Configuration
MATERIAL_ADMIN_SITE = {
    'HEADER': 'KatoMart Administration',
    'TITLE': 'KatoMart Admin',
    'MAIN_BG_COLOR': 'color: #2c3e50;',
    'MAIN_HOVER_COLOR': 'color: #34495e;',
    'SHOW_THEMES': True,
    'SHOW_COUNTS': True,
    'APP_ICONS': {
        'core': 'school',
        'auth': 'people',
    },
    'MODEL_ICONS': {
        'systemconfig': 'settings',
        'platform': 'web',
        'course': 'book',
        # ... more icons
    }
}
```

### Internationalization
Languages supported:
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Japanese (ja)
- Korean (ko)
- Chinese Simplified (zh-hans)
- Chinese Traditional (zh-hant)

### Custom Templates
Custom templates are located in `templates/admin/`:
- `base_site.html` - Base template with Material Design styling
- `index.html` - Dashboard with quick actions and system status
- `change_list.html` - Enhanced list views with better table styling
- `change_form.html` - Improved form layouts with fieldset organization

## Usage

### Dashboard
The admin dashboard provides:
- Quick access to common actions
- System status overview
- Recent activity feed
- Model-specific cards with counts

### Data Entry
- **Organized Fieldsets**: Related fields are grouped together
- **Inline Editing**: Related objects can be edited inline
- **Validation**: Real-time validation with helpful error messages
- **Auto-save**: Automatic saving of draft changes

### Data Management
- **Advanced Filtering**: Multiple filter options for each model
- **Search**: Full-text search across relevant fields
- **Bulk Operations**: Select multiple items for bulk actions
- **Export**: Export data in various formats

### Security
- **Encrypted Storage**: Sensitive data is encrypted at runtime
- **Permission-based Access**: Granular permissions for different user roles
- **Audit Trail**: All changes are logged with timestamps

## Customization

### Adding New Models
1. Create the model in `core/models.py`
2. Create an admin class in `core/admin.py`
3. Register the model with `@admin.register(ModelName)`
4. Add appropriate fieldsets and list displays

### Styling
The interface uses CSS variables for easy theming:
```css
:root {
    --primary-color: #1976d2;
    --primary-dark: #1565c0;
    --accent-color: #ff4081;
    --text-primary: #212121;
    --background: #fafafa;
    --surface: #ffffff;
}
```

### Adding Translations
1. Add new language to `LANGUAGES` in settings
2. Create locale directory: `locale/[lang]/LC_MESSAGES/`
3. Add translation strings to `django.po`
4. Compile translations: `python manage.py compilemessages`

## Testing

Run the test script to verify the setup:
```bash
python test_admin.py
```

This will check:
- Model registration
- Admin class configuration
- Template availability
- Settings configuration
- Internationalization setup

## Troubleshooting

### Common Issues

1. **Template Not Found**
   - Ensure `templates/` is in `TEMPLATES['DIRS']`
   - Check template file paths

2. **Static Files Not Loading**
   - Run `python manage.py collectstatic`
   - Check `STATIC_URL` and `STATIC_ROOT` settings

3. **Translation Not Working**
   - Ensure `USE_I18N = True`
   - Check locale file paths
   - Run `python manage.py compilemessages`

4. **Admin Interface Not Loading**
   - Check `INSTALLED_APPS` order
   - Verify all dependencies are installed
   - Check for import errors in admin.py

### Performance
- Use `list_select_related` for foreign key fields
- Implement `get_queryset` for custom filtering
- Use `readonly_fields` for computed values
- Consider pagination for large datasets

## Contributing

When adding new features:
1. Follow Material Design principles
2. Maintain responsive design
3. Add appropriate translations
4. Update documentation
5. Test across different screen sizes

## License

This admin interface is part of the KatoMart project and follows the same license terms. 