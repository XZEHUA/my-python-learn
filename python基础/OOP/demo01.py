#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 谢泽华
# @Date: 2026/3/8 11:55
# @Desc:

hello_python = 1

def func():
    print("demo01的func函数")

# 创建了一个类（自定义的数据类型）
class Hero:
    def __init__(self, name, hp, atk):
        self.name = name
        self.__hp = hp
        self.atk = atk

        print("self", self)

    def __str__(self):
        return str(self.__dict__)

    @property
    def hp(self):
        return self.__hp

    @hp.setter
    def hp(self, value):
        if value < 0 or value > 10000:
            return
        self.__hp = value

    def heal(self, hp = 300):
        self.__hp += hp
        print(f"【{self.name}】受到治疗，血量 + {hp}，当前血量{self.__hp}")

    def __damage(self, atk):
        self.__hp -= atk
        print(f"【{self.name}】受到伤害，血量 - {atk}，当前血量{self.__hp}")

    def a(self, target):
        if not target:
            print(f"【{self.name}】 A 空了")
            return
        print(f"【{self.name}】平 A 了一下 {target.name}，伤害{self.atk}")
        target.__damage(self.atk)


class HouYi(Hero):
    def __init__(self, name, hp, atk, shot_range):
        super().__init__(name, hp, atk)
        self.shot_range = shot_range

    def skill_3(self, target = None):
        if not target:
            print(f"【{self.name}】 大空了")
            return
        print(f'【{self.name}】大招晕住了 {target.name}')

    def a(self, target):
        print("射出了一箭")

class WuKong(Hero):
    def __init__(self, name, hp, atk, cr):
        super().__init__(name, hp, atk)
        self.shot_range = cr

    def skill_3(self, target = None):
        if not target:
            print(f"【{self.name}】 大空了")
            return
        print(f'【{self.name}】大招击飞了 {target.name}')

    def a(self, target):
        print("抡了一棒")


    def run(self, *speed):
        print("跑")


print(__name__)

if __name__ == '__main__':
    hy = HouYi("后羿", 3000, 100, 600)
    hy.heal(100)

    wk = WuKong("悟空", 3500, 200, 0.2)
    wk.heal(100)

    wk.hp = 10000
    print(wk.hp)

    wk.a(hy)
    hy.a(wk)

    wk.skill_3(hy)
    hy.skill_3(wk)


# 面向对象的三大特性：封装、继承、多态

# 封装
# 第一层封装：数据和操作绑定，所有行为必须经过对象
# 第二层封装：控制访问，防止乱改
# 第三层封装：隐藏实现，只暴露“能力”

# 继承：把共用的能力提到父类里，子类直接用，不用重复写

# 多态：接口一致，行为不同
# 重写（子类重写父类的方法）
# 重载（同一个类里面，方法名形同，参数或类型不同，Python 的重载是通过可变参数体现，更方便）