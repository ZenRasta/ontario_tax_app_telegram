# retirement_planner_app

Project description here.

## Debug API

For troubleshooting, the backend exposes a debug route listing registered
withdrawal strategies:

```
GET /api/v1/debug/strategies
```

The endpoint returns a JSON array of strategy codes such as `"GM"`.
