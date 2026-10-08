# coding: utf-8
import sys
def render_background(input_nk, start_frame=1, end_frame=10):
	import nuke
	"""后台渲染函数"""
	try:
		# 加载脚本
		nuke.scriptOpen(input_nk)
		nuke.execute("Write1", start_frame, end_frame)
		print("渲染完成！")
		return True
	except Exception as e:
		print("Error:{0}".format(e))
		return False


if __name__ == "__main__":
	args = sys.argv
	args.pop(0)
	for i in range(0,len(args),3):
		start_frame = int(args[i])
		end_frame = int(args[i+1])
		nk_path = args[i+2]
		print(start_frame)
		print(end_frame)
		print(nk_path)
		render_background(nk_path,start_frame,end_frame)
