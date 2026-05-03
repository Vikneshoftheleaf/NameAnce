import re
import asyncio
import dns.asyncresolver
import aiohttp
import random

class AdvancedDomainEngine:
    def __init__(self):
        self.prefixes = [
    'neo', 'omni', 'vivid', 'meta', 'prime', 'nova', 'flux', 'apex', 'zen', 'ultra',
    'alpha', 'arc', 'atlas', 'base', 'bold', 'bright', 'blue', 'core', 'clear', 'cloud',
    'cyber', 'data', 'deep', 'delta', 'digi', 'dyno', 'echo', 'edge', 'elite', 'epic',
    'ever', 'fast', 'fire', 'flow', 'focal', 'fuse', 'glow', 'grand', 'halo', 'hyper',
    'icon', 'infini', 'insta', 'intel', 'inter', 'ionic', 'iron', 'iso', 'jet', 'jump',
    'key', 'kind', 'koda', 'level', 'light', 'link', 'logic', 'lumina', 'macro', 'magna',
    'main', 'mass', 'max', 'mega', 'micro', 'mind', 'mint', 'mobi', 'mode', 'mono',
    'multi', 'nano', 'near', 'net', 'next', 'nexus', 'noble', 'north', 'nu', 'oak',
    'open', 'opti', 'orbit', 'origin', 'over', 'para', 'peak', 'pixel', 'poly', 'power',
    'pro', 'pulse', 'pure', 'quantum', 'quick', 'rapid', 'rare', 'real', 'sky', 'solar'
]
        self.suffixes = [
    'ly', 'ify', 'hub', 'labs', 'flow', 'grid', 'pulse', 'io', 'node', 'arc',
    'able', 'ally', 'ance', 'ary', 'base', 'bay', 'beat', 'bound', 'box', 'bridge',
    'cast', 'centric', 'chart', 'city', 'cloud', 'coast', 'conn', 'dash', 'deck', 'desk',
    'dock', 'done', 'door', 'dot', 'drive', 'ease', 'edge', 'ery', 'est', 'ethos',
    'field', 'fire', 'fix', 'fold', 'force', 'form', 'front', 'gear', 'gen', 'go',
    'gram', 'graph', 'growth', 'guru', 'hall', 'hive', 'hook', 'host', 'ism', 'ist',
    'it', 'ity', 'ize', 'joint', 'junction', 'key', 'kit', 'land', 'lane', 'layer',
    'line', 'link', 'list', 'logic', 'loop', 'mark', 'mart', 'mate', 'meet', 'mind',
    'nest', 'net', 'ops', 'pad', 'path', 'pilot', 'port', 'press', 'proof', 'run',
    'scale', 'scape', 'set', 'ship', 'site', 'space', 'stack', 'sync', 'vault', 'zone'
]
        self.stop_words = {
    'i', 'want', 'to', 'start', 'a', 'business', 'for', 'the', 'my', 'new', 'idea',
    'am', 'an', 'and', 'are', 'as', 'at', 'be', 'but', 'by', 'can', 'could', 'do',
    'does', 'for', 'from', 'get', 'give', 'go', 'had', 'has', 'have', 'he', 'her',
    'here', 'his', 'how', 'if', 'in', 'into', 'is', 'it', 'its', 'just', 'like',
    'make', 'me', 'more', 'most', 'my', 'no', 'not', 'of', 'on', 'one', 'or', 'our',
    'out', 'over', 'say', 'see', 'she', 'so', 'some', 'take', 'than', 'that', 'their',
    'them', 'then', 'there', 'these', 'they', 'this', 'those', 'through', 'too', 'under',
    'up', 'use', 'very', 'was', 'we', 'well', 'were', 'what', 'when', 'where', 'which',
    'while', 'who', 'will', 'with', 'would', 'you', 'your', 'about', 'company', 'startup',
    'services', 'agency', 'shop', 'store', 'online', 'selling', 'looking', 'build'
}

    def _get_seeds(self, description):
        words = re.sub(r'[^\u200B\w\s]', '', description.lower()).split()
        filtered_seeds = [w for w in words if w not in self.stop_words and len(w) > 2]
        random.shuffle(filtered_seeds) # Shuffle the seeds for randomization
        return filtered_seeds

    async def check_dns(self, domain):
        """Phase 1: Fast DNS Check (Checks if the domain resolves to an IP)"""
        resolver = dns.asyncresolver.Resolver()
        resolver.nameservers = ['8.8.8.8']
        try:
            await resolver.resolve(domain, 'A')
            return domain, False  # Taken (Has DNS records)
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            return domain, True   # Available (No DNS records found)
        except Exception:
            return domain, False  # Error/Timeout, assume unavailable or restricted

    async def verify_availability_deep(self, session, domain):
        """
        Phase 2: Deep Verification via Public API / RDAP
        This checks if the domain is registered with an ICANN registrar,
        even if it doesn't have an active DNS 'A' record (Parked/For Sale domains).
        """
        # Using a free RDAP/Whois public endpoint
        rdap_url = f"https://rdap.verisign.com/com/v1/domain/{domain}"
        try:
            async with session.get(rdap_url, timeout=3.0) as response:
                if response.status == 200:
                    data = await response.json()
                    # If it has an active event action like 'registration', it is taken.
                    events = data.get('events', [])
                    for event in events:
                        if event.get('eventAction') == 'registration':
                            return domain, False
                    return domain, True
                elif response.status == 404:
                    # 404 from Verisign RDAP indicates the domain does not exist in the registry
                    return domain, True
        except Exception:
            # Fallback to DNS-only status if the RDAP API is unreachable
            pass
        return domain, False

    async def run_engine(self, description, extension="com"):
        seeds = self._get_seeds(description)
        potential_names_all = set() # Use a temporary set to collect all possible generations

        if not seeds:
            print("❌ No keywords found.")
            return []

        # 1. Generation Phase
        # Generate all possible unique combinations from the provided lists
        for seed in seeds:
            # Combine with prefixes
            for p in self.prefixes:
                potential_names_all.add(f"{p}{seed}.{extension}")
            # Combine with suffixes
            for s in self.suffixes:
                potential_names_all.add(f"{seed}{s}.{extension}")

        # Randomize and limit to 100 potential names
        potential_names_list = list(potential_names_all)
        random.shuffle(potential_names_list) # Randomize the order
        potential_names = set(potential_names_list[:100]) # Take up to 100

        print(f"⚙️  Generated {len(potential_names)} potential names. Running Phase 1 (DNS)...")

        # 2. Run Phase 1 (DNS Check)
        dns_tasks = [self.check_dns(name) for name in potential_names]
        dns_results = await asyncio.gather(*dns_tasks)

        # Keep only domains that passed DNS availability
        potential_available = [name for name, is_avail in dns_results if is_avail]

        print(f"👉 Passed Phase 1: {len(potential_available)} names. Running Phase 2 (Deep Verification)...")

        # 3. Run Phase 2 (Deep Verification using aiohttp)
        async with aiohttp.ClientSession() as session:
            deep_tasks = [self.verify_availability_deep(session, name) for name in potential_available]
            deep_results = await asyncio.gather(*deep_tasks)

        final_available = [name for name, is_avail in deep_results if is_avail]
        return sorted(final_available, key=len)

# --- EXECUTION ---
# The execution part below is commented out to prevent it from running automatically
# when the cell is modified, as we are setting up an API.
# engine = AdvancedDomainEngine()
# user_input = "job alert"

# available_domains = await engine.run_engine(user_input)

# print(f"\n✅ VERIFIED AVAILABLE DOMAINS FOR: '{user_input}'\n" + "="*50)
# if not available_domains:
#     print("No domains fully verified as available.")
# else:
#     for i, name in enumerate(available_domains[:20], 1):
#         print(f"{i:2}. 🌟 {name}")