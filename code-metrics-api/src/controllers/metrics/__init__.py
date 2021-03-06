from flask import request, Blueprint, Response 
from src.dynamopipeline import pipelineMetrics 
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry,generate_latest, Info
import prometheus_client 
 
# Rota /metrics 
metrics = Blueprint('metrics',__name__) 
 
CONTENT_TYPE_LATEST = str('text/plain; version=0.0.4; charset=utf-8') 
 
registry = CollectorRegistry() 
 
SUM_PIPELINE      = Gauge('codemetrics_sum_pipeline', 'Total Pipelines',['provider'],registry=registry)
SUM_SUCCESS       = Gauge('codemetrics_sum_pipeline_success', 'Deployment successfully',['provider','account','pipeline'],registry=registry)
SUM_FAIL          = Gauge('codemetrics_sum_pipeline_failure', 'Deployment Failure',['provider','account','pipeline'],registry=registry)
DEPLOY_DAY        = Gauge('codemetrics_deploy_day', 'Deployment Frequency',['provider','account','pipeline','day'],registry=registry)
TIME_DEPLOY       = Gauge('codemetrics_time_deploy_seconds', 'Deployment Speedy',['provider', 'account','pipeline'],registry=registry)
TIME_STAGES       = Gauge('codemetrics_time_stage_seconds', 'Deployment Speedy',['provider', 'account','pipeline','stage'],registry=registry  )
TIME_ACTIONS      = Gauge('codemetrics_time_action_seconds', 'Deployment Speedy',['provider','account','pipeline','stage','action'],registry=registry)
PIPELINE_STATUS   = Gauge('codemetrics_pipeline_status','Status Pipeline',['provider','account','pipeline'],registry=registry)
ACTIONS_FAILD     = Gauge('codemetrics_time_actions_faild', 'Deployment Failure',['provider','account','pipeline','action'],registry=registry)
STAGES_FAILD      = Gauge('codemetrics_time_stages_faild',  'Deployment Failure',['provider','account','pipeline','stage'],registry=registry)
RUNTIME           = Info('codemetrics_runtime',  'technology',['provider','account','pipeline'],registry=registry)
PIPE_VERSION      = Info('codemetrics_pipe_version', 'Version Pipeline',['provider','account','pipeline'],registry=registry)
 
 
@metrics.route('')
@metrics.route('/') 
def codemetrics():
    
    # Recupera as metricas
    metrics = pipelineMetrics()

    if metrics:
    
       # total de pipeline
       for sum_pipeline in metrics['sum_pipeline']:
           SUM_PIPELINE.labels(sum_pipeline['provider']).set(sum_pipeline['max'])
       
       # Sum deploy of success
       for sum_success in metrics['sum_success']:
           SUM_SUCCESS.labels(sum_success['provider'],sum_success['projeto'],sum_success['app']).set(sum_success['max'])
       
       # Sum deploy of fail
       for sum_fail in metrics['sum_fail']:
           SUM_FAIL.labels(sum_fail['provider'],sum_fail['projeto'],sum_fail['app']).set(sum_fail['max'])
       
       # Sum deploy of today
       for deploy_day in metrics['deploy_day']:
           print(deploy_day)
           DEPLOY_DAY.labels(deploy_day['provider'],deploy_day['projeto'],deploy_day['app'],deploy_day['day']).set(deploy_day['qtd'])        
       
       # time of deploy
       for info_deploy in metrics['time_deploy']:
           TIME_DEPLOY.labels(info_deploy['provider'],info_deploy['projeto'],info_deploy['app']).set(info_deploy['deploytime'])
           
       # time from stage    
       for info_stages in metrics['time_stages']:
           TIME_STAGES.labels(info_stages['provider'],info_stages['projeto'],info_stages['app'],info_stages['stage']).set(info_stages['time'])
   
       # time from action 
       for info_action in metrics['time_actions']:
           TIME_ACTIONS.labels(info_action['provider'],info_action['projeto'],info_action['app'],info_action['stage'],info_action['action']).set(info_action['time'])
   
       # status da Pipeline
       for status in metrics['pipeline_status']:
          PIPELINE_STATUS.labels(status['provider'],status['projeto'],status['app']).set(status['status'])

       # stage faild
       for status in metrics['stages_fail']:
          STAGES_FAILD.labels(status['provider'],status['projeto'],status['app'],status['stage']).set(status['fail'])


       # action faild
       for status in metrics['actions_fail']:
          ACTIONS_FAILD.labels(status['provider'],status['projeto'],status['app'],status['action']).set(status['fail'])

       #pipe_runtime = []
       for status in metrics['runtime']:
          RUNTIME.labels(status['provider'],status['projeto'],status['app']).info({'runtime':status['runtime']})

       #pipe_version = []
       for status in metrics['pipe_version']:
          PIPE_VERSION.labels(status['provider'],status['projeto'],status['app']).info({'pipe_version':status['pipe_version']})


    return Response(prometheus_client.generate_latest(registry), mimetype=CONTENT_TYPE_LATEST)