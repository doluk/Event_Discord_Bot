# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 17:54:00 2020

@author: Lukas
"""
###############################################################################
# Imports
###############################################################################
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

###############################################################################
# Start the scheduler
###############################################################################
scheduler = AsyncIOScheduler(event_loop=asyncio.get_event_loop())
#jobstore = SQLAlchemyJobStore(url='postgresql+asyncpg://localhost:5432/team_utils')
jobstore = SQLAlchemyJobStore(url='sqlite:///jobs.db')
scheduler.add_jobstore(jobstore)
scheduler.start()

