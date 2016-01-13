# -*- coding: utf-8 -*-

from radiople.service import Service

from radiople.model.report import Report


class ReportService(Service):

    __model__ = Report


class ApiReportService(ReportService):

    pass

sevice = ReportService()
api_service = ApiReportService()
