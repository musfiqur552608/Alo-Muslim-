from django.core.cache import cache
from django.db import models

CONFIG_CACHE_KEY = "site_config"


class SiteConfig(models.Model):
    hijri_adjustment = models.SmallIntegerField(
        default=0,
        choices=[(-1, "-১ দিন"), (0, "সমন্বয় নেই"), (1, "+১ দিন")],
        help_text="বাংলাদেশের চাঁদ দেখা অনুযায়ী হিজরি তারিখ সমন্বয়",
    )

    class Meta:
        verbose_name = "সাইট কনফিগারেশন"

    def save(self, *args, **kwargs):
        self.pk = 1                   
        super().save(*args, **kwargs)
        cache.delete(CONFIG_CACHE_KEY)  

    @classmethod
    def load(cls) -> "SiteConfig":
        config = cache.get(CONFIG_CACHE_KEY)
        if config is None:
            config, _ = cls.objects.get_or_create(pk=1)
            cache.set(CONFIG_CACHE_KEY, config, 60 * 60)
        return config