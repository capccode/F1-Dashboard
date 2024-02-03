[
   {
      "essential": true,
      "name":"flask-app",
      "image":"${REPOSITORY_URL}",
      "portMappings":[
         {
            "containerPort":8050,
            "hostPort":8050,
            "protocol":"tcp"
         }
      ],
      "logConfiguration": {
          "logDriver": "awslogs",
          "options": {
            "awslogs-group": "${CLOUDWATCH_GROUP}",
            "awslogs-region": "${REGION}",
            "awslogs-stream-prefix": "ecs"
          }
        },
      "environment":[
         {
            "name":"FLASK_APP",
            "value":"${FLASK_APP}"
         },
         {
            "name":"FLASK_ENV",
            "value":"${FLASK_ENV}"
         },
         {
            "name":"APP_HOME",
            "value":"${FLASK_APP_HOME}"
         },
         {
            "name":"APP_PORT",
            "value":"${FLASK_APP_PORT}"
         }
      ]
   }
]