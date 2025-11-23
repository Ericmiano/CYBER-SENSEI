#!/usr/bin/env python
import os
os.chdir('backend')

with open('app/main.py', 'r') as f:
    content = f.read()

# Add import if not present
if 'from .seed import seed_database' not in content:
    content = content.replace(
        'from .database import create_tables',
        'from .database import create_tables\nfrom .seed import seed_database'
    )
    print('✓ Added seed import')

# Add seed call
if 'seed_database()' not in content:
    content = content.replace(
        '        print("✓ Database tables initialized")',
        '        print("✓ Database tables initialized")\n        seed_database()\n        print("✓ Database seeding completed")'
    )
    print('✓ Added seed_database() call')

with open('app/main.py', 'w') as f:
    f.write(content)

print('✓ main.py updated successfully')
