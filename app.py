#!/usr/bin/env python3
import os

import aws_cdk as cdk

import infra.config
from infra.infra_stack import FrontendStack, BackendStack



app = cdk.App()
env = app.node.try_get_context("env")
conf = infra.config.load(env)


FrontendStack(app, f"{conf.app_prefix}-frontend", conf=conf)
BackendStack(app, f"{conf.app_prefix}-backend", conf=conf)

app.synth()
