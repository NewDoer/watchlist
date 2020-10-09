#导入单元测试
from logging import setLogRecordFactory
from os import truncate
import unittest
from unittest import async_case
from unittest import result
from unittest.case import TestCase
# from flask_sqlalchemy import SQLAlchemy

from flask.cli import main
from flask.wrappers import Response
from watchlist import app,db
from watchlist.models import Movie,User
from watchlist.commands import forge,initdb

#TestCase测试案例，即用一组虚拟数据进行的测试
class WatchlistTestCase(unittest.TestCase):

    #初始测试固件
    def setUp(self):
        #更新配置
        app.config.update(TESTING=True,SQLALCHEMY_DATABASE_URI= 'sqlite:///:memory:')
        
        #创建数据库和表
        db.create_all()
        user = User(name='Test',username='test')
        user.set_password('123')
        movie = Movie(title= 'Test Movie Title',year='2019')

        db.session.add_all([user,movie])
        db.session.commit()

        #创建测试客户端
        self.client = app.test_client()
        #创建测试命令运行器
        self.runner = app.test_cli_runner()

    #结束测试固件
    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()

    def test_app_exist(self):
        self.assertIsNotNone(app)

    def test_app_is_testing(self):
        self.assertIsNotNone(app.config['TESTING'])

    #测试404页面
    def test_404_page(self):
        response = self.client.get('/nothing')
        data = response.get_data(as_text=True) #返回unicode数据
        self.assertIn('Page Not Found - 404',data)
        self.assertIn('Go Back',data)
        self.assertEqual(response.status_code,404) #判断相应状态

    #测试主页
    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('Test\'s Watchlist', data)
        self.assertIn('Test Movie Title',data)
        self.assertEqual(response.status_code,200)

    #测试辅助方法  Login 登录，这样才能测试在登录下的功能
    def login(self):
        self.client.post('/login',data=dict(
            username='test',
            password='123'),follow_redirects=True)

    #测试创建条目
    def test_create_item(self):
        self.login()

        #测试创建条目操作
        response = self.client.post('/',data=dict(
            title="New Movie",
            year='2019'
        ),follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item created.',data)
        self.assertIn('New Movie',data)

    #测试创建条目操作，但是电影标题为空
        response = self.client.post('/',data=dict(
            title="",
            year='2019'
        ),follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created.',data)
        self.assertIn('Invalid input',data)

     #测试创建条目操作，但是年份为空
        response = self.client.post('/',data=dict(
            title="New Movie",
            year=''
        ),follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item created.',data)
        self.assertIn('Invalid input',data)

    #测试更新条目
    def test_update_item(self):
        self.login()

        #测试更新页面
        response = self.client.get('/movie/edit/1')
        data = response.get_data(as_text=True)
        self.assertIn('Edit item',data)
        self.assertIn('Test Movie Title',data)
        self.assertIn('2019',data)

        #测试更新条目操作
        response = self.client.post('/movie/edit/1',data=dict(
            title = 'New Movie Edited',
            year='2019'
        ),follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item updated.',data)
        self.assertIn('New Movie Edited',data)

        #测试更新条目操作,但电影标题为空
        response = self.client.post('/movie/edit/1',data=dict(
            title = '',
            year='2019'
        ),follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item updated.',data)
        self.assertIn('Invalid input',data)  

         #测试更新条目操作,但年份为空
        response = self.client.post('/movie/edit/1',data=dict(
            title = 'New Movie Edited Again',
            year=''
        ),follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item updated.',data)
        self.assertNotIn('New Movie Edited Again',data)
        self.assertIn('Invalid input',data)

    #测试删除条目
    def test_delete_item(self):
        self.login()

        response = self.client.post('/movie/delete/1',follow_redirects=True)  
        data = response.get_data(as_text=True)
        self.assertIn('Item deleted',data)
        self.assertNotIn('Test Movie Title',data)


        #测试登录保护
    def test_login_protect(self):
        response = self.client.get('/')
        data= response.get_data(as_text =True)
        self.assertNotIn('Logout',data)
        self.assertNotIn('Settings',data)
        self.assertNotIn('<form method="post">',data)
        self.assertNotIn('Delete',data)
        self.assertNotIn('Edit',data)

        #测试登录
    def test_login(self):
        response = self.client.post('/login',data=dict(
        username = 'test',
        password='123'
        ),follow_redirects=True)
        data= response.get_data(as_text=True)
        self.assertIn('Login success',data)
        self.assertIn('Logout',data)
        self.assertIn('Settings',data)
        self.assertIn('Delete',data)
        self.assertIn('Edit',data)
        self.assertIn('<form method="POST">',data)
        
       
        #测试使用错误的密码登录
    # def test_login(self):
        response = self.client.post('/login',data=dict(
        username = 'test',
        password='456'
        ),follow_redirects=True)
        data= response.get_data(as_text=True)
        self.assertNotIn('Login success.',data)
        self.assertIn('Invalid username or password.',data) 

        #测试使用错误的用户名登录
        response = self.client.post('/login',data=dict(
        username = 'wrong',
        password='123'
        ),follow_redirects=True)
        data= response.get_data(as_text=True)
        self.assertNotIn('Login success.',data)
        self.assertIn('Invalid username or password.',data) 

        #测试使用空的用户名密码登录
        response = self.client.post('/login',data=dict(
        username = '',
        password=''
        ),follow_redirects=True)
        data= response.get_data(as_text=True)
        self.assertNotIn('Login success.',data)
        self.assertIn('Invalid input',data)

        #测试使用空的密码登录
        response = self.client.post('/login',data=dict(
        username = 'test',
        password=''
        ),follow_redirects=True)
        data= response.get_data(as_text=True)
        self.assertNotIn('Login success.',data)
        self.assertIn('Invalid input',data)

    #测试登出
    def test_logout(self):
        self.login()

        response = self.client.get('/logout',follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Goodbye',data)
        self.assertNotIn('Logout',data)
        self.assertNotIn('Settings',data)
        self.assertNotIn('Delete',data)
        self.assertNotIn('Edit',data)
        self.assertNotIn('<form method="POST">',data)
    
    #测试设置
    def test_settings(self):
        self.login()

        #测试设置页面
        response = self.client.get('/settings')
        data = response.get_data(as_text=True)
        self.assertIn('Settings',data)
        self.assertIn('Your name',data)

        #测试更新设置
        response = self.client.post('/settings',data=dict(
            name="Grey Li",
        ),follow_redirects= True)
        data = response.get_data(as_text=True)
        self.assertIn('Settings updated',data)
        self.assertIn('Grey Li',data)

        #测试更新设置，名字为空
        response = self.client.post('/settings',data=dict(
            name="",
        ),follow_redirects= True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Settings updated',data)
        self.assertIn('Invalid input',data)

    #测试虚拟数据
    def test_forge_command(self):
        result = self.runner.invoke(forge)
        self.assertIn('Done',result.output)
        self.assertNotEqual(Movie.query.count(),0)
    
    #测试初始化数据库
    def test_initdb_command(self):
        result = self.runner.invoke(initdb)
        self.assertIn('Initialized database',result.output)

    #测试生成管理员
    def test_admin_command(self):
        db.drop_all()
        db.create_all()
        result = self.runner.invoke(args=['admin','--username','grey','--password','123'])
        self.assertIn('Creating user',result.output)
        self.assertIn('Done',result.output)
        self.assertEqual(User.query.count(),1)
        self.assertEqual(User.query.first().username,'grey')
        self.assertTrue(User.query.first().validate_password('123'))

    #测试更新管理员账户
    def test_admin_command_update(self):

        result = self.runner.invoke(args=['admin','--username','peter','--password','456'])
        self.assertIn('Updating user',result.output)
        self.assertIn('Done',result.output)
        self.assertEqual(User.query.count(),1)
        self.assertEqual(User.query.first().username,'peter')
        self.assertTrue(User.query.first().validate_password('456'))
    

if __name__ == "__main__":
    unittest.main()