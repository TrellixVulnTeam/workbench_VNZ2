"""
 OpenVINO DL Workbench
 Class for storing int8 calibration errors

 Copyright (c) 2018 Intel Corporation

 LEGAL NOTICE: Your use of this software and any required dependent software (the “Software Package”) is subject to
 the terms and conditions of the software license agreements for Software Package, which may also include
 notices, disclaimers, or license terms for third party or open source software
 included in or with the Software Package, and your use indicates your acceptance of all such terms.
 Please refer to the “third-party-programs.txt” or other similarly-named text file included with the Software Package
 for additional details.
 You may obtain a copy of the License at
      https://software.intel.com/content/dam/develop/external/us/en/documents/intel-openvino-license-agreements.pdf
"""
from wb.main.console_tool_wrapper.error_message_processor import ErrorMessageProcessor


class ModelDownloaderErrorMessageProcessor(ErrorMessageProcessor):
    match_error = {
        'Caused by ProxyError Cannot connect to proxy': 'Network connection error. Check Internet connection. '
                                                        'If you are behind a corporate proxy, refer to documentation'
    }