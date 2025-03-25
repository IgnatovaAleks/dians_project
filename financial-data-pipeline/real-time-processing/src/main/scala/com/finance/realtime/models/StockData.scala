package com.finance.realtime.models

import java.sql.Timestamp

case class StockData(
  symbol: String,
  price: Double,
  volume: Long,
  timestamp: Timestamp,
  source: String
)