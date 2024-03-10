from app.libs import pyautoguiUtils
import os
import time
import sys
from app.state import loop

# if pyautoguiUtils.check(os.path.join("dy", "pub")):
#     if pyautoguiUtils.click(os.path.join("dy", "pub")):
#         print("task_success")
#     else:
#         print("点击发布按钮失败")
# else:
#     print("获取发布按钮失败")
# loop.bb['task'] = {}
# loop.bb['task']['data'] = {
#     "attachments": [
#         {
#             "filePath": "D:\\video",
#             "fileName": "1.mp4"
#         }
#     ],
#     "title": "testTitle",
#     "desc": "testDesc",
#     "topics": ["testTopics", "testTopics2"],
#     "friends": ["testFriends", "testFriends2"],
#     "addEvent": True,
#     "location": "杭州萧山机场",
#     "hotSpot": "西湖",
#     "needSync2OtherPlat": True,
#     "otherPlatTitle": "其他平台标题",     # 其他平台标题
#     "allow_save_video": "1",   # 允许保存视频   0 允许  1 不允许
#     "who_can_see": "1",   # 允许保存视频  0 公开 1 好友可见 2 仅自己可见
#     "pub_time": "1709154305",   # 发布时间
#
# }

if not pyautoguiUtils.check(os.path.join("dy", "sync_2_other_plat_switch_open")):
    print("add_location")
else:
    if pyautoguiUtils.click(os.path.join("dy", "sync_2_other_plat_switch_open")):
        pyautoguiUtils.scrollDown()
        print("add_location")
    else:
        print("开启同步到其他平台失败-already")