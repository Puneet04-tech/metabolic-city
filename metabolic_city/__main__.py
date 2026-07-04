"""
Entry point for running MetabolicCity AI as a module
"""

import asyncio
from metabolic_city.main import main

if __name__ == "__main__":
    asyncio.run(main())
