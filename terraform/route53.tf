data "aws_route53_zone" "primary" {
    name         = "lookmanolowo.com"
    private_zone = false
}

resource "aws_route53_record" "formula_1" {
  zone_id = data.aws_route53_zone.primary.zone_id
  name    = "f1.lookmanolowo.com"
  type    = "A"
  alias {
    name = aws_alb.alb.dns_name
    zone_id = aws_alb.alb.zone_id
    evaluate_target_health = true
  }
}