output "db_host" {
  value = aws_db_instance.mysql.address
}

output "ecs_cluster" {
  value = aws_ecs_cluster.main.name
}

output "alb_dns" {
  value = aws_lb.main.dns_name
}
