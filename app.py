#!/usr/bin/env python3
import os

import aws_cdk as cdk

import infra.config
from infra.infra_stack import FrontendStack, BackendStack, DNSStack, EdgeStack


app = cdk.App()
env = app.node.try_get_context("env")
conf = infra.config.load(env)

global_env = cdk.Environment(region="us-east-1")

dns_stack = DNSStack(app, f"{conf.app_prefix}-dns", conf=conf)
edge_stack = EdgeStack(app, f"{conf.app_prefix}-edge", conf=conf, env=global_env)
backend_stack = BackendStack(app, f"{conf.app_prefix}-backend", conf=conf)
frontend_stack = FrontendStack(app, f"{conf.app_prefix}-frontend", conf=conf, api_gw=backend_stack.api_gw, zone=dns_stack.zone, edge=edge_stack.edge_redirect)

app.synth()