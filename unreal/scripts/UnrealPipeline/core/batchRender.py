import unreal
import json
import os

class BatchRender:
    queues = []
    def __init__(self):
        self.movieSubsystem:unreal.MoviePipelineQueueSubsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
        self.movieSubsystemExecutor = unreal.MoviePipelinePIEExecutor(self.movieSubsystem)
        #链接到socket
        self.movieSubsystemExecutor.connect_socket("127.0.0.1",5060)
        #绑定回调函数
        self.movieSubsystemExecutor.on_individual_job_finished_delegate.add_callable_unique(self.on_individual_job_finished_delegate)
        self.movieSubsystemExecutor.on_individual_job_started_delegate.add_callable_unique(self.on_individual_job_started_delegate)
        self.movieSubsystemExecutor.on_individual_job_work_finished_delegate.add_callable_unique(self.on_individual_job_work_finished_delegate)
        self.movieSubsystemExecutor.on_executor_errored_delegate.add_callable_unique(self.on_executor_errored_delegate)
        self.movieSubsystemExecutor.on_executor_finished_delegate.add_callable_unique(self.on_executor_finished_delegate)
        self.movieSubsystemExecutor.set_is_rendering_offscreen(True)

    def RenderQueue(self,queue:unreal.MoviePipelineQueue):
        self.movieSubsystem.render_queue_with_executor_instance(self.movieSubsystemExecutor)


    #所有回调函数 
    def on_individual_job_started_delegate(self,job:unreal.MoviePipelineExecutorJob):
        #在此作业被用于初始化 UMoviePipeline 之前立即调用。
        message = dict(
            stage = "job",
            state = "start",
            job_name = job.job_name.split(".")[0],
            result = None,
            info = ""
        )
        self.movieSubsystemExecutor.send_socket_message(json.dumps(message))

    def on_individual_job_finished_delegate(self,job:unreal.MoviePipelineExecutorJob,success:bool):
        message = dict(
            stage = "job",
            state = "end",
            job_name = job.job_name.split(".")[0],
            result = success,
            info = ""
        )
        self.movieSubsystemExecutor.send_socket_message(json.dumps(message))


    def on_individual_job_work_finished_delegate(self,results:unreal.MoviePipelineOutputData):
        # 队列中每个作业完成后调用。参数结构体包含所有已写入文件的输出信息
        try:
            output_path = os.path.dirname(list(results.shot_data[0].render_pass_data.values())[0].file_paths[0])
        except:
            output_path = ""


        message = dict(
            stage = "job",
            state = "finish",
            job_name = results.job.job_name.split(".")[0],
            result = results.success,
            output_dir = output_path,
            info = output_path
        )
        self.movieSubsystemExecutor.send_socket_message(json.dumps(message))


    def on_executor_errored_delegate(self,pipeline_executor:unreal.MoviePipelineExecutorBase,pipeline_with_error:unreal.MoviePipeline,is_fatal:bool,error_text:unreal.Text):
        #当单个作业报告警告/错误时调用。如果严重程度足以中止作业（序列丢失、写入失败等），则作业被视为致命错误。
        message = dict(
            stage = "job",
            state = "Error",
            job_name = pipeline_with_error.get_current_job().job_name,
            result = False,
            info = error_text
        )
        self.movieSubsystemExecutor.send_socket_message(json.dumps(message))

    def on_executor_finished_delegate(self,pipeline_executor:unreal.MoviePipelineExecutorBase,success:bool):
        # 当整个队列渲染完成之后调用     
        message = dict(
            stage = "Queue",
            state = "end",
            job_name = "",
            result = True,
            info = ""
        )
        self.movieSubsystemExecutor.send_socket_message(json.dumps(message))
        unreal.SystemLibrary.quit_editor()
            

def RenderSequences(paths:list[str],config_path:str):
    subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
    queue = subsystem.get_queue()
    queue.delete_all_jobs()
    
    if not unreal.EditorAssetLibrary.does_asset_exist(config_path):
        unreal.SystemLibrary.quit_editor()
        return
    config = unreal.load_asset(config_path)

    for map_path, seq_path in zip(paths[::2], paths[1::2]):
        job = queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
        job.job_name = seq_path.split("/")[-1]

        job.map =  unreal.SoftObjectPath(map_path)
        job.sequence = unreal.SoftObjectPath(seq_path)

        if type(config) == unreal.MoviePipelinePrimaryConfig:
            job.set_configuration(config)
        elif type(config) == unreal.MovieGraphConfig:
            job.set_graph_preset(config)

            
    batch_render = BatchRender()
    batch_render.RenderQueue(queue)


if __name__ == "__main__":
    RenderSequences([
        "/Game/Shots/EP001/sc001/Ep001_sc001_001/Ep001_sc001_001_Map.Ep001_sc001_001_Map",
        "/Game/Shots/EP001/sc001/Ep001_sc001_001/Ep001_sc001_001_Render.Ep001_sc001_001_Render",
        "/Game/Shots/EP001/sc001/Ep001_sc001_002/Ep001_sc001_002_Map.Ep001_sc001_002_Map",
        "/Game/Shots/EP001/sc001/Ep001_sc001_002/Ep001_sc001_002_Render.Ep001_sc001_002_Render"
        ],"/Game/Pending_MoviePipelinePrimaryConfig")




    

