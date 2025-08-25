# DayCare Invoice Tracker - Modern Business Application

A professional Django web application for managing daycare invoices and payments, featuring a comprehensive light/dark theme system and modern UI/UX design.

## 🎨 Latest Features (v1.1.0)

**MAJOR UI/UX OVERHAUL - Modern Theme System:**

- 🌙 **Complete Light/Dark Theme System** with smooth transitions
- 🎨 **Professional Design System** with CSS custom properties
- 📱 **Fully Responsive Design** optimized for all devices
- ♿ **WCAG AA Accessibility** compliant with excellent contrast ratios
- 🚀 **Interactive Placeholder System** showing development roadmap
- ⚡ **Performance Optimized** with modern CSS and JavaScript
- ⌨️ **Enhanced Keyboard Navigation** with shortcuts and accessibility

## Phase 1 Objectives ✅

**Phase 1 Complete - Foundation & Modern UI:**

- ✅ Django project initialization with proper structure
- ✅ Custom user authentication system with working login/registration
- ✅ Core database models (User, Child, Invoice, Payment, DaycareProvider)
- ✅ Admin interface configuration with custom admin classes
- ✅ Modern responsive template system with Bootstrap 5
- ✅ Comprehensive light/dark theme system
- ✅ Professional business application design
- ✅ Interactive development roadmap communication
- ✅ Dashboard with beautiful statistics and placeholder functionality
- ✅ Full accessibility compliance and keyboard navigation

## Technology Stack

- **Backend**: Django 5.2.5, Python 3.10+
- **Database**: SQLite (development), PostgreSQL ready
- **Frontend**: Django templates with Bootstrap 5, modern CSS/JavaScript
- **UI/UX**: Complete light/dark theme system with CSS custom properties
- **Forms**: django-crispy-forms with Bootstrap styling
- **Configuration**: python-decouple for environment variables

## Project Structure

```
daycare_tracker/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── daycare_tracker/          # Main project configuration
│   ├── __init__.py
│   ├── settings.py          # Django settings with environment support
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py
├── accounts/                 # Custom user management
│   ├── models.py            # CustomUser model
│   ├── admin.py             # Admin configuration
│   ├── views.py             # Authentication views
│   ├── urls.py              # Account URLs
│   └── apps.py
├── invoices/                 # Invoice management
│   ├── models.py            # Invoice, Payment, Child, Provider models
│   ├── admin.py             # Admin configuration
│   ├── views.py             # Dashboard and list views
│   ├── urls.py              # Invoice URLs
│   ├── forms.py             # Forms for future development
│   ├── utils.py             # Utility functions for future PDF processing
│   └── apps.py
├── static/                   # Static files
│   ├── css/main.css         # Custom styles
│   ├── js/main.js           # Custom JavaScript
│   └── images/
├── templates/                # HTML templates
│   ├── base.html            # Base template with Bootstrap
│   ├── accounts/            # Authentication templates
│   │   ├── login.html
│   │   └── register.html
│   └── invoices/            # Invoice templates
│       ├── dashboard.html   # Main dashboard
│       ├── invoice_list.html
│       ├── payment_list.html
│       └── child_list.html
└── media/                    # Uploaded files
    └── invoices/
```

## Setup Instructions

### 1. Clone and Navigate
```bash
cd daycare_tracker
```

### 2. Environment Setup
```bash
# Copy environment template
copy .env.example .env

# Edit .env file with your settings (optional for development)
```

### 3. Install Dependencies
```bash
# Virtual environment is already configured
# Dependencies are already installed:
# - Django>=4.2
# - Pillow>=9.0
# - PyPDF2>=3.0 (for future PDF processing)
# - python-dateutil>=2.8
# - django-crispy-forms>=1.14
# - python-decouple>=3.6
# - django-extensions>=3.2
```

### 4. Database Setup
```bash
# Migrations have been created and applied
# Database: db.sqlite3

# Superuser created:
# Username: admin
# Email: admin@email.com
# Password: admin
```

### 5. Run Development Server
```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/ to access the application.

## Current Features (Phase 1)

### ✅ User Authentication
- Custom user model with email and phone fields
- User registration and login
- Password reset functionality (templates ready)
- Bootstrap-styled authentication forms

### ✅ Admin Interface
- Full admin access for all models
- Customized admin views with proper field organization
- Search and filtering capabilities
- Related object optimization

### ✅ Core Models
- **CustomUser**: Extended user model for future email integration
- **DaycareProvider**: Provider information with email automation fields
- **Child**: Child information linked to users and providers
- **Invoice**: Comprehensive invoice tracking with payment status
- **Payment**: Payment records with automatic status updates

### ✅ Dashboard
- User-specific statistics (children, invoices, payments)
- Recent invoices and payments display
- Outstanding balance calculation
- Quick action buttons (placeholder for Phase 2)
- Responsive design with Bootstrap 5

### ✅ Model Features
- Automatic payment status updates
- Calculated properties (total_paid, outstanding_balance)
- Proper model relationships with related_name
- Comprehensive validation and meta options

## Admin Interface

Access the admin at http://127.0.0.1:8000/admin/

**Superuser credentials:**
- Username: `admin`
- Password: `admin`

### Admin Features:
- User management with custom fields
- Daycare provider management
- Children registration and management  
- Invoice creation and tracking
- Payment recording
- Comprehensive search and filtering

## Model Relationships

```
CustomUser
├── Children (multiple per user)
    ├── Invoices (multiple per child)
        ├── Payments (multiple per invoice)

DaycareProvider
├── Children (multiple providers possible)
```

## Key Model Fields

### CustomUser
- Standard Django user fields
- `email` (unique, required)
- `phone_number`
- `notification_preferences` (JSON for future features)

### Child
- `user` (ForeignKey to CustomUser)
- `name`, `reference_number`
- `daycare_provider` (ForeignKey)
- `date_of_birth`
- `is_active`

### Invoice
- `child` (ForeignKey)
- `invoice_reference`
- Period dates (`period_start`, `period_end`)
- Financial fields (`original_amount`, `amount_due`, etc.)
- `payment_status` (unpaid/partial/paid/overdue)
- `pdf_file` (for future PDF uploads)
- Email automation fields (for future phases)

### Payment
- `invoice` (ForeignKey)
- `payment_date`, `amount_paid`
- `payment_method`
- `reference_number`, `notes`
- Auto-updates invoice payment status

## Future Development (Planned Phases)

### Phase 2: PDF Processing & Invoice Management
- PDF upload and text extraction
- Automatic invoice data parsing
- Invoice creation and editing forms
- Payment recording interface
- Enhanced dashboard with charts

### Phase 3: Advanced Features
- Email automation and IMAP integration
- Automatic invoice detection from emails
- Payment reminders and notifications
- Reporting and analytics
- Export functionality

### Phase 4: UI/UX Enhancement
- Advanced dashboard with charts
- Mobile-responsive improvements
- Search and filtering
- Bulk operations
- API endpoints

## Development Notes

### Django Best Practices Implemented
- Environment variable configuration
- Custom user model from the start
- Proper model relationships with related_name
- Comprehensive admin configuration
- Template inheritance and blocks
- Static file organization
- Security settings for development

### Design Patterns Used
- Class-based views for consistency
- Model managers for common queries
- Calculated properties for derived data
- Signal-like behavior in model save methods
- Comprehensive model validation

### Security Features
- CSRF protection enabled
- Proper authentication requirements
- File upload validation structure
- Environment variable usage
- Debug mode configuration

## Testing

To test the application:

1. **Admin Interface**: Visit `/admin/` and log in with superuser credentials
2. **User Registration**: Create a new user account
3. **Dashboard**: View the main dashboard with statistics
4. **Navigation**: Test all navigation links
5. **Models**: Create test data through admin to see dashboard populate

## Troubleshooting

### Common Issues:
- **ModuleNotFoundError**: Ensure virtual environment is activated
- **Database errors**: Run `python manage.py migrate`
- **Static files not loading**: Run `python manage.py collectstatic`
- **Permission errors**: Check file permissions in media directory

### Development Server:
```bash
# Check for issues
python manage.py check

# Run tests (when implemented)
python manage.py test

# Shell access for debugging
python manage.py shell
```

## Phase 1 Success Criteria ✅

- [x] Django project runs without errors
- [x] Admin interface accessible and functional
- [x] All models can be created/edited via admin
- [x] User authentication system works
- [x] Database relationships properly configured
- [x] Basic templates render correctly
- [x] Static files serve properly
- [x] Dashboard displays user-specific data
- [x] Model methods and properties work correctly
- [x] Environment configuration functional

## Next Steps

Phase 1 is complete! The foundation is solid and ready for Phase 2 development:

1. **PDF Processing**: Implement file upload and text extraction
2. **Form Development**: Create user-facing forms for invoice/payment management
3. **Enhanced Views**: Add create, edit, and detail views
4. **Dashboard Enhancement**: Add charts and more detailed statistics
5. **Testing**: Implement comprehensive test suite

The project follows Django best practices and the coding guidelines specified in `.github/copilot-instructions.md`.

---

**Project Status**: Phase 1 Complete ✅  
**Next Phase**: PDF Processing & Invoice Management  
**Framework**: Django 5.2.5 with Python 3.10+
