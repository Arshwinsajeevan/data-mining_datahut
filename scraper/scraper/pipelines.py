
import re
import json

class CleanPipeline:
    """Normalize phones, social keys, lists, and trim strings."""

    def process_item(self, item, spider):
        def clean_number(s):
            if not s:
                return ""
            s = s.strip()
            num = re.sub(r"[^\d+]", "", s)
            return num

        def clean_phone_list(lst):
            if not lst:
                return []
            cleaned = []
            for p in lst:
                if not p:
                    continue
                cleaned_p = clean_number(p)
                if cleaned_p:
                    cleaned.append(cleaned_p)
            return cleaned

        item['office_phone_numbers'] = clean_phone_list(item.get('office_phone_numbers') or [])
        item['agent_phone_numbers'] = clean_phone_list(item.get('agent_phone_numbers') or [])

        social = item.get('social') or {}
        social.setdefault('facebook_url', "")
        social.setdefault('twitter_url', "")
        social.setdefault('linkedin_url', "")
        item['social'] = social
        langs = item.get('languages')
        if langs is None:
            item['languages'] = []
        elif isinstance(langs, list):
            item['languages'] = [l.strip() for l in langs if isinstance(l, str) and l.strip()]
        else:
            item['languages'] = [langs.strip()] if isinstance(langs, str) and langs.strip() else []

        for k, v in list(item.items()):
            if isinstance(v, str):
                item[k] = v.strip()
        
            if v is None:
                if k in ('office_phone_numbers', 'agent_phone_numbers', 'languages'):
                    item[k] = []
                else:
                    item[k] = ""

        return item
