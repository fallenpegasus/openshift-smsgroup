from setuptools import setup

setup(name='SMSGroup',
      version='1.0',
      description='SMS Group Broadcast using Twilio and OpenShift',
      author='Mark Atwood',
      author_email='matwood@redhat.com',
      url='http://www.python.org/sigs/distutils-sig/',
      install_requires=['twilio', 'pymongo'],
     )
