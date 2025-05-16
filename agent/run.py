from src.agent import Agent
import asyncio

if __name__ == "__main__":
    ag = Agent()
    asyncio.run(ag.run())
