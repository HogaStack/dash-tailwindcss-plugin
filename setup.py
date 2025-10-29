from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

with open('requirements.txt', 'r', encoding='utf-8') as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith('#')]

setup(
    name='dash-tailwindcss-plugin',
    version='0.1.3',
    author='insistence',
    author_email='3055204202@qq.com',
    homepage='https://github.com/HogaStack/dash-tailwindcss-plugin',
    description='A Dash plugin for integrating TailwindCSS using Dash 3.x hooks',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/HogaStack/dash-tailwindcss-plugin',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Framework :: Dash',
    ],
    python_requires='>=3.8',
    install_requires=requirements,
    extras_require={
        'dev': [
            'build',
            'twine',
        ],
        'test': [
            'pytest>=6.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'dash-tailwindcss-plugin=dash_tailwindcss_plugin.cli:main',
        ],
    },
)
