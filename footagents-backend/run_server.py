#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "footagents.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 