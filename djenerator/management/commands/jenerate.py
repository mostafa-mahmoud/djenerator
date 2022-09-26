from django.core.management.base import BaseCommand

from djenerator import generate_test_data


class Command(BaseCommand):
    help = "Generates random test data for an app using djenerator."

    def add_arguments(self, parser):
        parser.add_argument("app-name", type=str)
        parser.add_argument(
            "size", type=int, help="Number of instance per model"
        )
        parser.add_argument(
            "--allow-null", action="store_true",
            help="decide of allowing null values"
        )
        parser.add_argument(
            "--models", type=str, default=None, nargs="*",
            help="Generate data for a specific set of models."
        )
        parser.add_argument(
            "--allow-external-instances", action="store_true",
            help=(
                "decide if related fields can be linked to already existing mo"
                "dels, otherwise, they restricted to the ones being generated."
            )
        )

    def handle(self, *args, **options):
        size = int(options["size"])
        app_name = options["app-name"]
        models_cls = options["models"]
        allow_null = bool(options["allow_null"])
        allow_external_instances = bool(options["allow_external_instances"])

        generate_test_data(
            app_name, size, allow_null=allow_null, models_cls=models_cls,
            allow_external_instances=allow_external_instances
        )
