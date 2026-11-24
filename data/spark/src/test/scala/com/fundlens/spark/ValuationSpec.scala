package com.fundlens.spark

import org.apache.spark.sql.SparkSession
import org.scalatest.BeforeAndAfterAll
import org.scalatest.funsuite.AnyFunSuite

class ValuationSpec extends AnyFunSuite with BeforeAndAfterAll {

  private lazy val spark = SparkSession.builder().master("local[2]").appName("test").getOrCreate()
  import spark.implicits._

  override def afterAll(): Unit = spark.stop()

  private def positions = Seq(
    ("2026-11-20", "FL-0001", BigDecimal(125000), BigDecimal("48250.75"), "FR0000120271", BigDecimal(12000)),
    ("2026-11-20", "FL-0001", BigDecimal(125000), BigDecimal("48250.75"), "FR0000131104", BigDecimal(8500)),
    ("2026-11-20", "FL-0001", BigDecimal(125000), BigDecimal("48250.75"), "US0378331005", BigDecimal(1500)),
    ("2026-11-23", "FL-0001", BigDecimal(125000), BigDecimal("48250.75"), "FR0000120271", BigDecimal(12000)),
    ("2026-11-23", "FL-0001", BigDecimal(125000), BigDecimal("48250.75"), "FR0000131104", BigDecimal(8500)),
    ("2026-11-23", "FL-0001", BigDecimal(125000), BigDecimal("48250.75"), "US0378331005", BigDecimal(1500))
  ).toDF("as_of", "fund_id", "shares_outstanding", "cash", "isin", "quantity")

  private def prices = Seq(
    ("2026-11-20", "FR0000120271", "EUR", BigDecimal("61.42")),
    ("2026-11-20", "FR0000131104", "EUR", BigDecimal("74.18")),
    ("2026-11-20", "US0378331005", "USD", BigDecimal("228.35")),
    ("2026-11-23", "FR0000120271", "EUR", BigDecimal("63.00")),
    ("2026-11-23", "FR0000131104", "EUR", BigDecimal("72.50")),
    ("2026-11-23", "US0378331005", "USD", BigDecimal("230.00"))
  ).toDF("as_of", "isin", "currency", "close")

  private def fx = Seq(("2026-11-20", "USD", BigDecimal("0.92")), ("2026-11-23", "USD", BigDecimal("0.92")))
    .toDF("as_of", "currency", "rate_to_eur")

  test("VL identique à fund-api et à dbt") {
    val navs = Valuation.nav(Valuation.valuePositions(positions, prices, fx))
      .orderBy("as_of").select("nav_per_share").as[BigDecimal].collect().toSeq
    assert(navs == Seq(BigDecimal("13.8476"), BigDecimal("13.9032")))
  }

  test("contributions par titre") {
    val c = Valuation.contributions(Valuation.valuePositions(positions, prices, fx), "2026-11-20", "2026-11-23")
      .select("isin", "contribution").as[(String, Double)].collect().toMap
    assert(c("FR0000120271") == 0.010954)
    assert(c("FR0000131104") == -0.00825)
  }

  test("cours manquant refusé") {
    val sansApple = prices.filter($"isin" =!= "US0378331005")
    val e = intercept[IllegalStateException](Valuation.valuePositions(positions, sansApple, fx))
    assert(e.getMessage.contains("US0378331005"))
  }
}
