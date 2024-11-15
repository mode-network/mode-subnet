from datetime import datetime

from pydantic import BaseModel, Field


class SimulationInput(BaseModel):
    asset: str = Field(default="BTC", description="The asset to simulate.")
    start_time: datetime = Field(default_factory=datetime.now, description="The start time of the simulation.")
    time_increment: int = Field(..., description="Time increment in seconds.")
    time_length: int = Field(..., description="Total time length in seconds.")
    num_simulations: int = Field(..., description="Number of simulation runs.")
    sigma: float = Field(..., description="Standard deviation of the simulation.", default=0.01)
