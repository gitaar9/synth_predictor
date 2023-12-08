from setuptools import setup, find_packages

setup(
    name='synth_predictor',
    version='0.1.0',
    packages=find_packages(),  # Automatically discover and include all packages
    install_requires=[
        # List your dependencies here
    ],
    entry_points={
        'console_scripts': [
            # Add any command-line scripts here if applicable
        ],
    },
    author='Your Name',
    author_email='your.email@example.com',
    description='A brief description of your package',
    long_description='A longer description of your package',
    long_description_content_type='text/markdown',
    url='https://github.com/your_username/your_package_name',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
