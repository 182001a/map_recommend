```mermaid
erDiagram
  CustomUser ||--o{ RouteSession : "owns"
  RouteSession ||--|{ RouteSpot   : "has"
  RouteSession ||--o{ RoutePhoto  : "has"
```