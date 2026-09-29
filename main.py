# -*- coding: utf-8 -*-
"""健身日志 App - 界面层（Kivy 2.3.1）"""
import os
import platform
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.metrics import dp, sp

import db

# Windows 注册中文字体
if platform.system() == 'Windows':
    _font = 'C:/Windows/Fonts/msyh.ttc'
    if os.path.exists(_font):
        LabelBase.register('Roboto', fn_regular=_font, fn_bold=_font)

# 主题色
BG = (0.07, 0.08, 0.09, 1)
CARD = (0.114, 0.129, 0.149, 1)
TEXT = (0.93, 0.93, 0.93, 1)
SUB = (0.54, 0.57, 0.61, 1)
ACC = (0.58, 0.83, 0.82, 1)
WARN = (0.96, 0.70, 0.58, 1)


def hex_to_rgba(h):
    h = h.lstrip('#')
    r = int(h[0:2], 16) / 255
    g = int(h[2:4], 16) / 255
    b = int(h[4:6], 16) / 255
    return (r, g, b, 1)


KV = """
<Card@BoxLayout>:
    canvas.before:
        Color:
            rgba: 0.114, 0.129, 0.149, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [12,]
    padding: dp(12)
    spacing: dp(6)
    size_hint_y: None
    height: self.minimum_height

<NumBtn@Button>:
    background_color: 0.58, 0.83, 0.82, 0.25
    color: 0.93, 0.98, 0.98, 1
    font_size: sp(13)
    size_hint_y: None
    height: dp(44)

<MenuBtn@Button>:
    background_color: 0.114, 0.13, 0.15, 1
    color: 0.93, 0.98, 0.98, 1
    font_size: sp(14)
    size_hint_y: None
    height: dp(48)
    canvas.before:
        Color:
            rgba: 0.24, 0.28, 0.32, 0.6
        Line:
            rounded_rectangle: (self.x, self.y, self.width, self.height, 10)
            width: 1

<SmallL@Label>:
    font_size: sp(12)
    color: 0.54, 0.57, 0.61, 1
    size_hint_y: None
    height: dp(20)

<TitleL@Label>:
    font_size: sp(17)
    bold: True
    color: 0.93, 0.98, 0.98, 1
    size_hint_y: None
    height: dp(30)

ScreenManager:
    id: sm
    TodayScreen:
        name: 'today'
    DietScreen:
        name: 'diet'
    WorkoutScreen:
        name: 'workout'
    CycleScreen:
        name: 'cycle'
    TdeeScreen:
        name: 'tdee'
"""


def make_scroll(content, spacing=8):
    sv = ScrollView(do_scroll_x=False, bar_width=dp(4))
    box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=spacing,
                    padding=[dp(12), dp(12), dp(12), dp(12)])
    box.bind(minimum_height=box.setter('height'))
    content.size_hint_y = None
    content.bind(minimum_height=content.setter('height'))
    box.add_widget(content)
    sv.add_widget(box)
    return sv


def make_nav_bar(manager):
    nav = BoxLayout(orientation='horizontal', spacing=dp(3), size_hint_y=None,
                    height=dp(50), padding=[dp(4), dp(4), dp(4), dp(4)])
    for name, scr in [("今日", 'today'), ("饮食", 'diet'), ("训练", 'workout'),
                      ("周期", 'cycle'), ("TDEE", 'tdee')]:
        b = Button(text=name, background_color=(0.2, 0.22, 0.25, 1),
                   color=(0.58, 0.83, 0.82, 1), font_size=sp(13))
        b.bind(on_release=lambda inst, s=scr: setattr(manager, 'current', s))
        nav.add_widget(b)
    return nav


def make_screen(screen, manager):
    layout = BoxLayout(orientation='vertical')
    layout.add_widget(screen)
    layout.add_widget(make_nav_bar(manager))
    return layout


def make_popup(title, content_box, width=0.9):
    popup = Popup(title=title, content=content_box,
                  size_hint=(width, 0.7),
                  background_color=(0.09, 0.10, 0.11, 1),
                  separator_color=hex_to_rgba("#94D4D0"),
                  title_color=(0.93, 0.93, 0.93, 1))
    close_btn = Button(text="关闭", size_hint_y=None, height=dp(44),
                       background_color=(0.3, 0.3, 0.35, 1))
    close_btn.bind(on_release=lambda inst: popup.dismiss())
    content_box.add_widget(close_btn)
    return popup


def card_box():
    box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(6))
    box.bind(minimum_height=box.setter('height'))
    return box


def stat_card(title, value, sub=""):
    c = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80),
                  padding=[dp(12), dp(10), dp(12), dp(10)])
    with c.canvas.before:
        Color(rgba=CARD)
        Rectangle(pos=c.pos, size=c.size)
    c.bind(pos=lambda inst, v: setattr(c.canvas.before.children[0], 'pos', v))
    c.bind(size=lambda inst, v: setattr(c.canvas.before.children[0], 'size', v))
    c.add_widget(Label(text=title, font_size=sp(12), color=SUB,
                       size_hint_y=None, height=dp(20)))
    c.add_widget(Label(text=value, font_size=sp(22), color=ACC,
                       size_hint_y=None, height=dp(30)))
    if sub:
        c.add_widget(Label(text=sub, font_size=sp(11), color=SUB,
                           size_hint_y=None, height=dp(18)))
    return c


# ============ 今日页面 ============
class TodayScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.layout = BoxLayout(orientation='vertical')
        self.scroll = make_scroll(card_box())
        self.layout.add_widget(self.scroll)
        self.layout.add_widget(make_nav_bar(self.manager if hasattr(self, 'manager') else None))

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.refresh())

    def refresh(self):
        sm = self.parent
        if sm:
            self.layout.clear_widgets()
            content = card_box()

            today = db.today_str()
            foods = db.get_foods(today)
            total_kcal = sum(f['kcal'] or 0 for f in foods)
            body = db.get_body(today)

            content.add_widget(stat_card("今日热量", f"{int(total_kcal)} kcal",
                                         f"已记录 {len(foods)} 条饮食"))

            if body:
                content.add_widget(stat_card("今日体重",
                                             f"{body['weight']:.1f} kg" if body['weight'] else "未记录",
                                             f"体脂 {body['bodyfat']:.1f}%" if body['bodyfat'] else ""))
            else:
                content.add_widget(stat_card("今日体重", "未记录", "点击下方记录"))

            btn_weight = Button(text="记录体重", size_hint_y=None, height=dp(44),
                                background_color=(0.2, 0.4, 0.5, 1))
            btn_weight.bind(on_release=lambda inst: self.show_weight_popup())
            content.add_widget(btn_weight)

            self.layout.add_widget(make_scroll(content))
            self.layout.add_widget(make_nav_bar(sm))

    def show_weight_popup(self):
        box = BoxLayout(orientation='vertical', spacing=dp(8), padding=[dp(12), dp(12), dp(12), dp(12)])
        box.add_widget(Label(text="体重 (kg)", font_size=sp(14), color=SUB, size_hint_y=None, height=dp(30)))
        ti_w = TextInput(input_filter='float', font_size=sp(18), size_hint_y=None, height=dp(44))
        box.add_widget(ti_w)
        box.add_widget(Label(text="体脂率 (%)", font_size=sp(14), color=SUB, size_hint_y=None, height=dp(30)))
        ti_bf = TextInput(input_filter='float', font_size=sp(18), size_hint_y=None, height=dp(44))
        box.add_widget(ti_bf)

        def save(inst):
            w = float(ti_w.text) if ti_w.text else None
            bf = float(ti_bf.text) if ti_bf.text else None
            if w:
                db.save_body(db.today_str(), w, bf or 0)
            popup.dismiss()
            self.refresh()

        save_btn = Button(text="保存", size_hint_y=None, height=dp(44),
                          background_color=(0.2, 0.5, 0.4, 1))
        save_btn.bind(on_release=save)
        box.add_widget(save_btn)

        popup = Popup(title="记录体重", content=box, size_hint=(0.9, 0.6),
                      background_color=(0.09, 0.10, 0.11, 1),
                      separator_color=hex_to_rgba("#94D4D0"),
                      title_color=(0.93, 0.93, 0.93, 1))
        close_btn = Button(text="关闭", size_hint_y=None, height=dp(44),
                           background_color=(0.3, 0.3, 0.35, 1))
        close_btn.bind(on_release=lambda inst: popup.dismiss())
        box.add_widget(close_btn)
        popup.open()


# ============ 饮食页面 ============
class DietScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(lambda dt: self.refresh())

    def refresh(self):
        sm = self.parent
        if not sm:
            return
        self.clear_widgets()
        content = card_box()

        today = db.today_str()
        foods = db.get_foods(today)
        total_kcal = sum(f['kcal'] or 0 for f in foods)
        total_p = sum(f['protein'] or 0 for f in foods)
        total_c = sum(f['carb'] or 0 for f in foods)
        total_f = sum(f['fat'] or 0 for f in foods)

        content.add_widget(stat_card("今日饮食总览",
                                     f"{int(total_kcal)} kcal",
                                     f"P:{int(total_p)}g C:{int(total_c)}g F:{int(total_f)}g"))

        for f in foods:
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50),
                            spacing=dp(4))
            with row.canvas.before:
                Color(rgba=CARD)
                Rectangle(pos=row.pos, size=row.size)
            row.bind(pos=lambda inst, v, r=row: setattr(r.canvas.before.children[0], 'pos', v))
            row.bind(size=lambda inst, v, r=row: setattr(r.canvas.before.children[0], 'size', v))

            info = Label(text=f"{f['name'] or ''}\n{int(f['kcal'] or 0)}kcal",
                         font_size=sp(12), color=TEXT, halign='left')
            info.bind(size=lambda inst, v: setattr(inst, 'text_size', v))
            row.add_widget(info)

            del_btn = Button(text="×", size_hint_x=0.2,
                             background_color=(0.5, 0.2, 0.2, 1))
            del_btn.bind(on_release=lambda inst, fid=f['id']: self.del_food(fid))
            row.add_widget(del_btn)
            content.add_widget(row)

        add_btn = Button(text="+ 添加食物", size_hint_y=None, height=dp(48),
                         background_color=(0.2, 0.4, 0.5, 1))
        add_btn.bind(on_release=lambda inst: self.add_food_popup())
        content.add_widget(add_btn)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(make_scroll(content))
        layout.add_widget(make_nav_bar(sm))
        self.add_widget(layout)

    def del_food(self, fid):
        db.delete_food(fid)
        self.refresh()

    def add_food_popup(self):
        box = BoxLayout(orientation='vertical', spacing=dp(6), padding=[dp(12), dp(12), dp(12), dp(12)])
        box.add_widget(Label(text="食物名称", font_size=sp(12), color=SUB, size_hint_y=None, height=dp(24)))
        ti_name = TextInput(font_size=sp(16), size_hint_y=None, height=dp(40))
        box.add_widget(ti_name)
        box.add_widget(Label(text="热量 (kcal)", font_size=sp(12), color=SUB, size_hint_y=None, height=dp(24)))
        ti_kcal = TextInput(input_filter='float', font_size=sp(16), size_hint_y=None, height=dp(40))
        box.add_widget(ti_kcal)
        box.add_widget(Label(text="碳水 (g)", font_size=sp(12), color=SUB, size_hint_y=None, height=dp(24)))
        ti_c = TextInput(input_filter='float', font_size=sp(16), size_hint_y=None, height=dp(40))
        box.add_widget(ti_c)
        box.add_widget(Label(text="蛋白质 (g)", font_size=sp(12), color=SUB, size_hint_y=None, height=dp(24)))
        ti_p = TextInput(input_filter='float', font_size=sp(16), size_hint_y=None, height=dp(40))
        box.add_widget(ti_p)
        box.add_widget(Label(text="脂肪 (g)", font_size=sp(12), color=SUB, size_hint_y=None, height=dp(24)))
        ti_f = TextInput(input_filter='float', font_size=sp(16), size_hint_y=None, height=dp(40))
        box.add_widget(ti_f)

        def save(inst):
            name = ti_name.text.strip()
            kcal = float(ti_kcal.text) if ti_kcal.text else 0
            carb = float(ti_c.text) if ti_c.text else 0
            protein = float(ti_p.text) if ti_p.text else 0
            fat = float(ti_f.text) if ti_f.text else 0
            if name:
                db.add_food(db.today_str(), "", name, kcal, carb, protein, fat, 0)
            popup.dismiss()
            self.refresh()

        save_btn = Button(text="保存", size_hint_y=None, height=dp(44),
                          background_color=(0.2, 0.5, 0.4, 1))
        save_btn.bind(on_release=save)
        box.add_widget(save_btn)

        popup = Popup(title="添加食物", content=box, size_hint=(0.9, 0.85),
                      background_color=(0.09, 0.10, 0.11, 1),
                      separator_color=hex_to_rgba("#94D4D0"),
                      title_color=(0.93, 0.93, 0.93, 1))
        close_btn = Button(text="关闭", size_hint_y=None, height=dp(44),
                           background_color=(0.3, 0.3, 0.35, 1))
        close_btn.bind(on_release=lambda inst: popup.dismiss())
        box.add_widget(close_btn)
        popup.open()


# ============ 训练页面 ============
class WorkoutScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(lambda dt: self.refresh())

    def refresh(self):
        sm = self.parent
        if not sm:
            return
        self.clear_widgets()
        content = card_box()

        today = db.today_str()
        db.ensure_workout(today)
        wo = db.get_workout(today)
        exercises = db.get_exercises(today)

        content.add_widget(stat_card("今日训练",
                                     f"{len(exercises)} 个动作",
                                     wo.get('aerobic', '') or "无有氧"))

        for ex in exercises:
            sets = db.get_sets(ex['id'])
            sets_text = " / ".join(
                f"{s['weight']}x{s['reps']}" for s in sets if s['weight'] and s['reps']) or "暂无组次"
            row = BoxLayout(orientation='vertical', size_hint_y=None,
                            height=dp(60), padding=[dp(8), dp(4), dp(8), dp(4)])
            with row.canvas.before:
                Color(rgba=CARD)
                Rectangle(pos=row.pos, size=row.size)
            row.bind(pos=lambda inst, v, r=row: setattr(r.canvas.before.children[0], 'pos', v))
            row.bind(size=lambda inst, v, r=row: setattr(r.canvas.before.children[0], 'size', v))

            row.add_widget(Label(text=ex['ex_name'], font_size=sp(14), color=ACC,
                                 size_hint_y=None, height=dp(22)))
            row.add_widget(Label(text=sets_text, font_size=sp(12), color=SUB,
                                 size_hint_y=None, height=dp(20)))
            content.add_widget(row)

        add_ex_btn = Button(text="+ 添加动作", size_hint_y=None, height=dp(48),
                             background_color=(0.2, 0.4, 0.5, 1))
        add_ex_btn.bind(on_release=lambda inst: self.add_exercise_popup())
        content.add_widget(add_ex_btn)

        # 有氧记录
        box_aerobic = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(48), spacing=dp(4))
        ti_ae = TextInput(text=wo.get('aerobic', '') or '', hint_text="有氧内容",
                          font_size=sp(14), size_hint_x=0.7)
        box_aerobic.add_widget(ti_ae)
        save_ae_btn = Button(text="保存有氧", size_hint_x=0.3,
                             background_color=(0.2, 0.5, 0.4, 1))
        def save_ae(inst):
            db.save_workout(today, ti_ae.text.strip(),
                           wo.get('state', 0) if wo else 0,
                           wo.get('fatigue', 0) if wo else 0)
            self.refresh()
        save_ae_btn.bind(on_release=save_ae)
        box_aerobic.add_widget(save_ae_btn)
        content.add_widget(box_aerobic)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(make_scroll(content))
        layout.add_widget(make_nav_bar(sm))
        self.add_widget(layout)

    def add_exercise_popup(self):
        box = BoxLayout(orientation='vertical', spacing=dp(6), padding=[dp(12), dp(12), dp(12), dp(12)])
        box.add_widget(Label(text="动作名称", font_size=sp(12), color=SUB, size_hint_y=None, height=dp(24)))
        ti_name = TextInput(font_size=sp(16), size_hint_y=None, height=dp(40))
        box.add_widget(ti_name)

        def save(inst):
            name = ti_name.text.strip()
            if name:
                db.add_exercise(db.today_str(), name)
            popup.dismiss()
            self.refresh()

        save_btn = Button(text="添加", size_hint_y=None, height=dp(44),
                          background_color=(0.2, 0.5, 0.4, 1))
        save_btn.bind(on_release=save)
        box.add_widget(save_btn)

        popup = Popup(title="添加动作", content=box, size_hint=(0.9, 0.5),
                      background_color=(0.09, 0.10, 0.11, 1),
                      separator_color=hex_to_rgba("#94D4D0"),
                      title_color=(0.93, 0.93, 0.93, 1))
        close_btn = Button(text="关闭", size_hint_y=None, height=dp(44),
                           background_color=(0.3, 0.3, 0.35, 1))
        close_btn.bind(on_release=lambda inst: popup.dismiss())
        box.add_widget(close_btn)
        popup.open()


# ============ 周期页面 ============
class CycleScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(lambda dt: self.refresh())

    def refresh(self):
        sm = self.parent
        if not sm:
            return
        self.clear_widgets()
        content = card_box()

        cycles = db.get_cycles()
        content.add_widget(stat_card("训练周期", f"{len(cycles)} 个周期", ""))

        for cy in cycles:
            row = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(70),
                            padding=[dp(8), dp(4), dp(8), dp(4)])
            with row.canvas.before:
                Color(rgba=CARD)
                Rectangle(pos=row.pos, size=row.size)
            row.bind(pos=lambda inst, v, r=row: setattr(r.canvas.before.children[0], 'pos', v))
            row.bind(size=lambda inst, v, r=row: setattr(r.canvas.before.children[0], 'size', v))

            row.add_widget(Label(text=cy['name'] or '', font_size=sp(14), color=ACC,
                                 size_hint_y=None, height=dp(24)))
            row.add_widget(Label(text=f"{cy['start_date']} ~ {cy['end_date']}",
                                 font_size=sp(12), color=SUB, size_hint_y=None, height=dp(20)))
            del_btn = Button(text="删除", size_hint_y=None, height=dp(28),
                            background_color=(0.5, 0.2, 0.2, 1))
            del_btn.bind(on_release=lambda inst, cid=cy['id']: self.del_cycle(cid))
            row.add_widget(del_btn)
            content.add_widget(row)

        add_btn = Button(text="+ 新建周期", size_hint_y=None, height=dp(48),
                         background_color=(0.2, 0.4, 0.5, 1))
        add_btn.bind(on_release=lambda inst: self.add_cycle_popup())
        content.add_widget(add_btn)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(make_scroll(content))
        layout.add_widget(make_nav_bar(sm))
        self.add_widget(layout)

    def del_cycle(self, cid):
        db.delete_cycle(cid)
        self.refresh()

    def add_cycle_popup(self):
        box = BoxLayout(orientation='vertical', spacing=dp(6), padding=[dp(12), dp(12), dp(12), dp(12)])
        box.add_widget(Label(text="周期名称", font_size=sp(12), color=SUB, size_hint_y=None, height=dp(24)))
        ti_name = TextInput(font_size=sp(16), size_hint_y=None, height=dp(40))
        box.add_widget(ti_name)
        box.add_widget(Label(text="开始日期 (YYYY-MM-DD)", font_size=sp(12), color=SUB, size_hint_y=None, height=dp(24)))
        ti_start = TextInput(font_size=sp(16), size_hint_y=None, height=dp(40))
        box.add_widget(ti_start)
        box.add_widget(Label(text="结束日期 (YYYY-MM-DD)", font_size=sp(12), color=SUB, size_hint_y=None, height=dp(24)))
        ti_end = TextInput(font_size=sp(16), size_hint_y=None, height=dp(40))
        box.add_widget(ti_end)

        def save(inst):
            name = ti_name.text.strip()
            if name and ti_start.text and ti_end.text:
                db.add_cycle(name, ti_start.text.strip(), ti_end.text.strip())
            popup.dismiss()
            self.refresh()

        save_btn = Button(text="创建", size_hint_y=None, height=dp(44),
                          background_color=(0.2, 0.5, 0.4, 1))
        save_btn.bind(on_release=save)
        box.add_widget(save_btn)

        popup = Popup(title="新建周期", content=box, size_hint=(0.9, 0.7),
                      background_color=(0.09, 0.10, 0.11, 1),
                      separator_color=hex_to_rgba("#94D4D0"),
                      title_color=(0.93, 0.93, 0.93, 1))
        close_btn = Button(text="关闭", size_hint_y=None, height=dp(44),
                           background_color=(0.3, 0.3, 0.35, 1))
        close_btn.bind(on_release=lambda inst: popup.dismiss())
        box.add_widget(close_btn)
        popup.open()


# ============ TDEE 页面 ============
class TdeeScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(lambda dt: self.refresh())

    def refresh(self):
        sm = self.parent
        if not sm:
            return
        self.clear_widgets()
        content = card_box()

        body = db.get_body()
        w = body['weight'] if body and body['weight'] else 65
        bf = body['bodyfat'] if body and body['bodyfat'] else 20

        content.add_widget(stat_card("TDEE 计算器", "填写参数计算", ""))

        box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
        box.bind(minimum_height=box.setter('height'))

        box.add_widget(Label(text="体重 (kg)", font_size=sp(12), color=SUB, size_hint_y=None, height=dp(24)))
        ti_w = TextInput(text=str(w), input_filter='float', font_size=sp(16), size_hint_y=None, height=dp(40))
        box.add_widget(ti_w)

        box.add_widget(Label(text="体脂率 (%)", font_size=sp(12), color=SUB, size_hint_y=None, height=dp(24)))
        ti_bf = TextInput(text=str(bf), input_filter='float', font_size=sp(16), size_hint_y=None, height=dp(40))
        box.add_widget(ti_bf)

        box.add_widget(Label(text="活动系数", font_size=sp(12), color=SUB, size_hint_y=None, height=dp(24)))
        ti_act = TextInput(text="1.55", input_filter='float', font_size=sp(16), size_hint_y=None, height=dp(40))
        box.add_widget(ti_act)
        box.add_widget(Label(text="久坐1.2 轻度1.375 中度1.55 高度1.725", font_size=sp(10), color=SUB, size_hint_y=None, height=dp(20)))

        result_label = Label(text="", font_size=sp(14), color=ACC, size_hint_y=None, height=dp(100),
                             halign='left', valign='top')
        result_label.bind(size=lambda inst, v: setattr(inst, 'text_size', v))

        def calc(inst):
            try:
                weight = float(ti_w.text) if ti_w.text else 65
                bodyfat = float(ti_bf.text) if ti_bf.text else 20
                activity = float(ti_act.text) if ti_act.text else 1.55
                r = db.calc_tdee(weight, bodyfat, activity, "maintain")
                result_label.text = (f"BMR: {r['bmr']} kcal\n"
                                     f"TDEE: {r['tdee']} kcal\n"
                                     f"维持: {r['target']} kcal\n"
                                     f"蛋白质: {r['protein_g']}g\n"
                                     f"碳水: {r['carb_g']}g\n"
                                     f"脂肪: {r['fat_g']}g")
            except Exception:
                result_label.text = "输入有误"

        calc_btn = Button(text="计算", size_hint_y=None, height=dp(44),
                          background_color=(0.2, 0.5, 0.4, 1))
        calc_btn.bind(on_release=calc)
        box.add_widget(calc_btn)
        box.add_widget(result_label)
        content.add_widget(box)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(make_scroll(content))
        layout.add_widget(make_nav_bar(sm))
        self.add_widget(layout)


class FitLogApp(App):
    def build(self):
        self.title = "健身日志"
        Window.clearcolor = BG
        sm = Builder.load_string(KV)
        sm.current = 'today'
        return sm

    def on_start(self):
        sm = self.root
        if sm and sm.current:
            try:
                sm.get_screen(sm.current).refresh()
            except Exception:
                pass


if __name__ == '__main__':
    FitLogApp().run()
