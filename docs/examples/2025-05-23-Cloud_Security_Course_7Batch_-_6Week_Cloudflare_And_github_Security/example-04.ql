/**
 * @name SQL Injection 취약점 탐지
 * @description 사용자 입력이 SQL 쿼리에 직접 삽입되는 경우를 탐지합니다.
 * @kind path-problem
 * @problem.severity error
 * @security-severity 9.8
 */

import javascript
import DataFlow::PathGraph

class SqlInjectionConfig extends TaintTracking::Configuration {
  SqlInjectionConfig() { this = "SqlInjectionConfig" }

  override predicate isSource(DataFlow::Node source) {
    exists(Express::RequestExpr req |
      source.asExpr() = req.getAPropertyRead(["query", "body", "params"])
    )
  }

  override predicate isSink(DataFlow::Node sink) {
    exists(DatabaseQuery query | sink.asExpr() = query.getAQueryArgument())
  }
}

from SqlInjectionConfig config, DataFlow::PathNode source, DataFlow::PathNode sink
where config.hasFlowPath(source, sink)
select sink.getNode(), source, sink, "사용자 입력이 SQL 쿼리에 직접 삽입됩니다."
