from setuptools import setup

setup(name='deye_inverter',
      version='0.1',
      description='Pulls data from a Deye inverter and pushes it to an MQTT topic',
      url='https://github.com/BrydonLeonard/DeyeInverter',
      author='Brydon Leonard',
      author_email='brydon.leonard@gmail.com',
      license='GPLv3',
      packages=[],
      zip_safe=False,
      install_requires=['libscrc', 'paho-mqtt'])