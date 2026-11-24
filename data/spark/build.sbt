ThisBuild / scalaVersion := "2.12.20"
ThisBuild / organization := "com.fundlens"

val sparkVersion = "3.5.3"

lazy val root = (project in file("."))
  .settings(
    name := "fundlens-spark",
    libraryDependencies ++= Seq(
      "org.apache.spark" %% "spark-sql" % sparkVersion % Provided,
      "org.scalatest" %% "scalatest" % "3.2.19" % Test
    ),
    Test / fork := true,
    Test / javaOptions ++= Seq("--add-opens=java.base/sun.nio.ch=ALL-UNNAMED", "--add-opens=java.base/java.nio=ALL-UNNAMED"),
    assembly / assemblyJarName := "fundlens-spark-assembly.jar"
  )
