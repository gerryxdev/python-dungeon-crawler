# v2 draft

import sys
import time
import random
import copy

version = "0.0.099"

def typ(text, delay=0.01):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

# base player class

class Player:
    def __init__(self,name,charname,endurance,perception,strength,dexterity,wisdom,willpower):
        self.name = name
        self.charname = charname
        self.endurance = endurance
        self.perception = perception
        self.strength = strength
        self.dexterity = dexterity
        self.wisdom = wisdom
        self.willpower = willpower

        self.inventory = []
        self.gold = 0
        self.roomscompleted = 0
        self.monsterkills = 0
        self.dungeondepth = 0

        self.hp = int(7 + endurance*1.2)
        self.max_hp = self.hp
        self.ini = int(2 + (perception + dexterity)/2)
        self.dodge = int (5+ dexterity/3)
        self.tohit = int (50+ dexterity*0.8)
        self.wisdom_tohit = int(40 + wisdom * 0.8)
        self.willpower_tohit = int(40 + willpower * 0.8)
        self.critbase = int(5 + perception * 0.3)
        self.defence = 0
        self.active_effects = []

        self.bleedresist = int(endurance * 0.6 + strength * 0.4)
        self.blightresist = int(endurance * 0.5 + willpower * 0.5)
        self.magicresist = int(wisdom * 0.6 + willpower * 0.4)
        self.fireresist = int(strength * 0.4 + willpower * 0.6)
        self.lightresist = int(endurance * 0.3 + willpower * 0.7)
        self.darkresist = int(-5 + (wisdom * 0.4 + willpower * 0.6))

        self.equipment = {
            'mainarm': None,
            'sidearm': None,
            'armorslot': None,
            'neckslot': None,
            'leftring': None,
            'rightring': None,
            'trinket': None
        }

        self.abilities = {
            'slot_1': None,
            'slot_2': None,
            'slot_3': None,
            'slot_4': None,
        }

########### Methode zur Ausgabe von Charakter Grundwerten

    def __str__(self):       
        return f"\n|| {self.name} ||\n|| HP: {self.hp}  INI: {self.ini}  Dodge: {self.dodge}  Base ToHIT: {self.tohit} ||\n|| END: {self.endurance}  PER: {self.perception}  STR: {self.strength}  DEX: {self.dexterity}  WIS: {self.wisdom}  WIL: {self.willpower} ||"


hero1 = Player(
    name="Gebrochener Ritter",
    charname = "Unbekannter",
    endurance = 15,
    perception = 8,
    strength = 12,
    dexterity = 7,
    wisdom = 5,
    willpower=6
)

hero2 = Player(
    name="Bettlerin",
    charname = "Unbekannte",
    endurance=6,
    perception=12,
    strength=5,                    ######## für Tests, original Wert == 5
    dexterity=10,
    wisdom=12,
    willpower=9
)

hero3 = Player(
    name="Geistlicher",
    charname = "Unbekannter",
    endurance=12,
    perception=9,
    strength=8,
    dexterity=7,
    wisdom=8,
    willpower=10
)

hero4 = Player(
    name="Jägersmann",
    charname = "Unbekannter",
    endurance=10,
    perception=14,
    strength=8,
    dexterity=10,
    wisdom=5,
    willpower=7
)

###########################################################################################################################

class Item:
    def __init__(self, name, description, value, tier=0):
        self.name = name
        self.description = description
        self.value = value
        self.tier = tier
        


# potion = Item (
#     name = "Kleiner Heiltrank",
#      healing_power= 8
# )

class Weapon(Item):
    def __init__(self, name, description, tohitmod, damage, stancedmg, strscaling, min_var, max_var, reqs=None, value=0, tier=0):
        super().__init__(name,description, value, tier)
        self.tohitmod = tohitmod
        self.damage = damage
        self.strscaling = strscaling    
        self.stancedmg = stancedmg
        self.min_var = min_var
        self.max_var = max_var
        self.reqs =  reqs if reqs else {} 



### Get damage versuch für scaling mit waffen | !!! Wichtig !!! , unter die class, vor den objects ###

    def getdamage(self, player):
            return self.damage + int(player.strength * self.strscaling)


###########################################################################################################################

noobsknightsword = Weapon(
    name = 'Rostiges Langschwert',
    description= 'Ein schartiges altes Schwert, fast stumpf und mit Rostflecken übersäht.',
    tohitmod = +5,
    damage = 4,
    strscaling = 0.2,
    stancedmg = 4,          ######## für Tests, original Wert == 4
    min_var = -1,
    max_var = 1,

    reqs={"strength":6},
    value= 1,
    tier=0
)

ballancedsword = Weapon(
    name = 'Ausgewogenes Langschwert',
    description= 'Ein anständiges Langschwert, ohne Zierde. Es liegt gut in der Hand.',
    tohitmod = +8,
    damage = 5,
    strscaling = 0.3,
    stancedmg = 4.5,
    min_var = 1,
    max_var = 2,

    reqs={"strength":8},
    value= 12,
    tier=1
)

witcheschoice = Weapon(
    name = 'Verbogenes Kurzschwert',
    description='Eine krude Klinge mit verbogener Spitze. Verdellt und ohne Parierstange',
    tohitmod = +8,
    damage = 4,
    strscaling = 0.1,
    stancedmg = 1,
    min_var = -1,
    max_var = 1,

    reqs={"strength": 4, "dexterity": 5},
    value= 4,
    tier=0
)

fineshortsword = Weapon(
    name = 'Scharfes Kurzschwert',
    description='Eine Waffe feiner Machart, leicht und anständig gewichtet.',
    tohitmod = +12,
    damage = 5,
    strscaling = 0.18,
    stancedmg = 2,
    min_var = 0,
    max_var = 1,

    reqs={"strength": 5, "dexterity": 9},
    value= 10,
    tier=1
)

woodclub = Weapon(
    name = 'Einfach Holzkeule',
    description= 'Primitive Waffe aus stabilem Holz mit einfachem Ledergriff.',
    tohitmod = +6,
    damage = 5,
    strscaling = 0.35,
    stancedmg = 6,
    min_var = -1,
    max_var = 2,

    reqs={"strength": 8},
    value= 4,
    tier=1
)

oldhalberd = Weapon(
    name = 'Ausgediente Hellebarde',
    description= 'EIne schwere und zierlose Stangenwaffe. Alt, aber immernoch einsatzfähig.',
    tohitmod = +8,
    damage = 6,
    strscaling = 0.3,
    stancedmg = 5.5,
    min_var = 0,
    max_var = 2,

    reqs={"strength": 10, "dexterity": 8},
    value= 25,
    tier=1
)

ironmace = Weapon(
    name = 'Eiserner Streitkolben',
    description= 'Nicht besonders handlich oder hübsch, aber ein wuchtiges Mordwerkzeug.',
    tohitmod = +7,
    damage = 6,
    strscaling = 0.35,
    stancedmg = 6.5,
    min_var = -1,
    max_var = 2,

    reqs={"strength": 10},
    value= 14,
    tier=1
)

noobhuntersaxe = Weapon(
    name = 'Schartige Axt',
    description='Eignet sich hervorragend zum Schlagen von Holz. Und zum Spalten von Schädeln.',
    tohitmod = +8,
    damage = 5,
    strscaling = 0.3,
    stancedmg = 5,
    min_var = -1,
    max_var = 2,

    reqs={'strength': 10, 'dexterity': 10},
    value= 10,
    tier=1

)

woodflail = Weapon(
    name = 'Modriger Flegel',
    description= 'Das Holz ist morsch, aber die Waffe liegt gut in der Hand und ist brauchbar genug.',
    tohitmod = +6,
    damage = 4,
    strscaling = 0.2,
    stancedmg = 6,
    min_var = 0,
    max_var = 1,

    reqs={'strength':8},
    value=6,
    tier=0
)

###########################################################################################################################

class StatusEffect:
    def __init__(self, name, dmg_per_turn=0, duration=0, message="", effect_type="neutral", stat_mod=None, activates_ability=False, cast_ability=None, 
                 trigger_event=None, consume_on_trigger=False):
        self.name = name
        self.dmg_per_turn = dmg_per_turn
        self.duration = duration
        self.message = message
        self.effect_type = effect_type
        self.stat_mod = stat_mod or {}
        
        self.activates_ability = activates_ability
        self.cast_ability = cast_ability
        self.trigger_event = trigger_event
        self.consume_on_trigger = consume_on_trigger

    def on_apply(self, target):
        if self.stat_mod:
            for stat, value in self.stat_mod.items():
                if hasattr(target, stat):
                    current_val = getattr(target, stat)
                    setattr(target, stat, current_val + value)

    def tick(self, target):
        if self.duration > 0:
            if self.dmg_per_turn != 0:
                target.hp -= self.dmg_per_turn
                typ(f"[{self.name}] {self.message} ({self.dmg_per_turn} Schaden).")
            
            self.duration -= 1
        
        # Duration fix Update implementiert
        return self.duration > 0

    def on_remove(self, target):
        if self.stat_mod:
            for stat, value in self.stat_mod.items():
                if hasattr(target, stat):
                    current_val = getattr(target, stat)
                    setattr(target, stat, current_val - value)
            typ(f"Die Wirkung von {self.name} lässt nach.")

#################### Status Effekt Draft Templates

template_bleeding_claws = StatusEffect(
    name="KlauenBlutung", 
    dmg_per_turn=1, 
    duration=2, 
    message="Du blutest!", 
    effect_type="bleed", # Wichtig für die Zuweisung zum blight_resist
    stat_mod= None
)

template_tar = StatusEffect(
    name="Teer", 
    dmg_per_turn=1, 
    duration=2, 
    message="Der zähe Schlamm brennt!", 
    effect_type="blight", # Wichtig für die Zuweisung zum blight_resist
    stat_mod={"defence": -1}
)

retreat_buff = StatusEffect(
    name="Rückzug",
    dmg_per_turn=0,
    duration=1,
    message="Die Kreatur geht in Deckung. + 5 auf Ausweichen!",
    effect_type="buff",
    stat_mod={"dodge": 5} 
)
###########################################################################################################################

class Ability:
    def __init__(self, name, tohitmod, hit_count=1, is_consumable=False, max_charges=0, 
                 apply_to_self=False, is_attack=True, break_on_miss=False):
        self.name = name
        self.tohitmod = tohitmod
        self.hit_count = hit_count
        self.is_consumable = is_consumable
        self.max_charges = max_charges
        self.current_charges = max_charges
        self.apply_to_self = apply_to_self
        self.is_attack = is_attack
        self.break_on_miss = break_on_miss

    def use(self, user, target, weapon):
        if self.is_consumable:
            if self.current_charges <= 0:
                typ(f"\nKeine Ladungen mehr für {self.name}!")
                return False
            self.current_charges -= 1
        return self.resolve(user, target, weapon)
    
###########################################################################################################################

class WeaponAbility(Ability):
    def __init__(self, name, tohitmod, min_mod, max_mod, stancedmg, hit_count=1, 
                 apply_to_self=False, status_effect=None, ov_dmg=None, ov_dur=None, 
                 base_apply_chance=100, is_attack=True, break_on_miss=False):
        super().__init__(name, tohitmod, hit_count, apply_to_self=apply_to_self, 
                         is_attack=is_attack, break_on_miss=break_on_miss)
        self.min_mod = min_mod
        self.max_mod = max_mod
        self.stancedmg = stancedmg
        self.status_effect = status_effect
        self.ov_dmg = ov_dmg
        self.ov_dur = ov_dur
        self.base_apply_chance = base_apply_chance

    def resolve(self, user, target, weapon):
        ### Für Buffs / Heals / Status etc
        if not self.is_attack:
            if self.status_effect:
                new_effect = copy.deepcopy(self.status_effect)
                if self.ov_dmg is not None: new_effect.dmg_per_turn = self.ov_dmg
                if self.ov_dur is not None: new_effect.duration = self.ov_dur
                
                # Geht immer auf den User, da es kein Angriff ist
                new_effect.on_apply(user)
                user.active_effects.append(new_effect)
                typ(f"\n>> {self.name}! {user.name} konzentriert sich. ({new_effect.name} aktiv)")
            return True

        ### Standard Angriffstyp
        total_dmg = 0
        total_stance_dmg = 0
        hits = 0

        for i in range(self.hit_count):
            hit_chance = int((user.tohit + weapon.tohitmod) * self.tohitmod) - target.dodge
            
            # Treffer
            if random.randint(1, 100) <= hit_chance:
                base_phys = weapon.getdamage(user)
                w_roll = random.randint(weapon.min_var, weapon.max_var)
                a_mod = random.uniform(self.min_mod, self.max_mod)
                
                dmg = max(int((base_phys + w_roll) * a_mod) - target.defence, 1)
                s_dmg = int(weapon.stancedmg * self.stancedmg)
                
                target.hp -= dmg
                target.stance -= s_dmg
                total_dmg += dmg
                total_stance_dmg += s_dmg
                hits += 1

                # STATUS PRO TREFFER APPLIZIEREN
                if self.status_effect:
                    resist_attr = f"{self.status_effect.effect_type}_resist"
                    resist_value = getattr(target, resist_attr, 0)
                    final_chance = self.base_apply_chance - resist_value

                    if self.apply_to_self or random.randint(1, 100) <= final_chance:
                        new_effect = copy.deepcopy(self.status_effect)
                        if self.ov_dmg is not None: new_effect.dmg_per_turn = self.ov_dmg
                        if self.ov_dur is not None: new_effect.duration = self.ov_dur
                        
                        apply_target = user if self.apply_to_self else target
                        new_effect.on_apply(apply_target)
                        apply_target.active_effects.append(new_effect)
                        
                        msg = "Buff gestapelt!" if self.apply_to_self else "Debuff appliziert!"
                        if self.hit_count > 1: typ(f"  [Stack {hits}] {new_effect.name}: {msg}")
            
            # Fehlschlag
            else:
                if self.hit_count > 1:
                    typ(f"  -> Schlag {i+1} geht daneben!")
                # COMBO BREAKER CHECK
                if self.break_on_miss:
                    if self.hit_count > 1: typ("  -> Die Angriffsserie wurde unterbrochen!")
                    break 
        
        # Auswertung
        if hits > 0:
            if self.hit_count > 1:
                typ(f"\n>> {self.name}! Gesamt: {total_dmg} Schaden ({hits} Treffer). {target.name} verliert {total_stance_dmg} Stance.")
            else:
                typ(f"\n>> {self.name}! {total_dmg} Schaden. {target.name} verliert {total_stance_dmg} Stance.")
            return True
        else:
            typ(f"\n>> {self.name} verfehlt komplett!")
            return False


swiftstrike = WeaponAbility (
    name = 'Leichter Angriff',
    tohitmod = 1.3,
    min_mod = 0.7,
    max_mod = 0.7,
    stancedmg = 0.8
)

heavystrike = WeaponAbility (
    name = 'Schwerer Angriff',
    tohitmod = 0.8,
    min_mod = 1.1,
    max_mod = 1.8,
    stancedmg = 1.65
)

ballancedstrike = WeaponAbility (
    name = 'Ausgewogener Hieb',
    tohitmod = 1,
    min_mod = 1.0,
    max_mod = 1.2,
    stancedmg = 1.1
)

impale = WeaponAbility (
    name = 'Aufspiessen',
    tohitmod = 1,
    min_mod = 1.0,
    max_mod = 1.5,
    stancedmg = 0.7
)

finesse = WeaponAbility (
    name = 'Finesse',
    tohitmod = 1.2,
    min_mod = 0.8,
    max_mod = 0.9,
    stancedmg = 0.4
)

pound = WeaponAbility (
    name = 'Wuchtschlag',
    tohitmod = 1.0,
    min_mod = 1.0,
    max_mod = 1.1,
    stancedmg = 2
)

dividingstrike = WeaponAbility (
    name = 'Spalten',
    tohitmod = 0.9,
    min_mod = 0.9,
    max_mod = 1.3,
    stancedmg = 1.2
)

######################################### Colossal_Counter_Set ###############################

hidden_colossal_counter = WeaponAbility(
    name="Kolossaler Gegenschlag",
    tohitmod=1.5,
    min_mod=2.0,
    max_mod=3.5,
    stancedmg=3,
    is_attack=True
)

colossal_counter_status = StatusEffect(
    name="Angriffshaltung",
    duration=1,
    stat_mod={"defence": 5, "dodge": -10},
    activates_ability=True,
    cast_ability=hidden_colossal_counter,
    trigger_event="after_enemy",
    consume_on_trigger=True
)

colossal_counter = WeaponAbility (
    name = 'Kolossaler Gegenschlag',
    tohitmod = 0,
    min_mod = 0,
    max_mod = 0,
    stancedmg = 0,
    is_attack=False,
    apply_to_self=True,
    status_effect=colossal_counter_status
)
######################################### Colossal_Counter_Set ###############################

adummy3 = WeaponAbility (
    name = 'dummy3',
    tohitmod = 1,
    min_mod = 1.0,
    max_mod = 1.0,
    stancedmg = 1
)

###########################################################################################################################

class SpellAbility(Ability):
    def __init__(self, name, tohitmod, base_dmg, wis_scaling, flat_var, flat_stance, 
                 charges, hit_count=1, apply_to_self=False, status_effect=None, 
                 ov_dmg=None, ov_dur=None, base_apply_chance=100, 
                 is_attack=True, break_on_miss=False):
        
        # Ladungslogik und Basis Parameter an Mutterklasse
        super().__init__(name, tohitmod, hit_count=hit_count, 
                         is_consumable=True, max_charges=charges, 
                         apply_to_self=apply_to_self, is_attack=is_attack, 
                         break_on_miss=break_on_miss)
        
        # Original Parameter
        self.base_dmg = base_dmg
        self.wis_scaling = wis_scaling
        self.flat_var = flat_var
        self.flat_stance = flat_stance
        
        # Neue System Parameter
        self.status_effect = status_effect
        self.ov_dmg = ov_dmg
        self.ov_dur = ov_dur
        self.base_apply_chance = base_apply_chance

    def resolve(self, user, target, weapon=None):
        # --- 1. SONDERFALL: UTILITY (is_attack=False) ---
        if not self.is_attack:
            if self.status_effect:
                new_effect = copy.deepcopy(self.status_effect)
                if self.ov_dmg is not None: new_effect.dmg_per_turn = self.ov_dmg
                if self.ov_dur is not None: new_effect.duration = self.ov_dur
                new_effect.on_apply(user)
                user.active_effects.append(new_effect)
                typ(f"\n>> {self.name}! Eine magische Aura erfüllt {user.name}.")
            return True

        # --- 2. REGULÄRER ANGRIFFS-ZAUBER (Shotgun-Logik) ---
        total_dmg = 0
        total_stance_dmg = 0
        hits = 0

        # Wichtig: Weapon-Bonus einbeziehen wie im Original
        weapon_bonus = getattr(weapon, 'wisdom_tohit', 0) if weapon else 0

        for i in range(self.hit_count):
            hit_chance = int((user.wisdom_tohit + weapon_bonus) * self.tohitmod) - target.dodge
            
            if random.randint(1, 100) <= hit_chance:
                # --- DEINE ORIGINAL SCHADENSFORMEL ---
                total_base = self.base_dmg + (user.wisdom * self.wis_scaling)
                s_roll = random.randint(0, self.flat_var)
                # Magie ignoriert die halbe Rüstung!
                dmg = max(int(total_base + s_roll) - int(target.defence * 0.5), 1)
                
                target.hp -= dmg
                target.stance -= self.flat_stance
                total_dmg += dmg
                total_stance_dmg += self.flat_stance
                hits += 1

                # STATUS-LOGIK (Applizierung pro Treffer)
                if self.status_effect:
                    resist_attr = f"{self.status_effect.effect_type}_resist"
                    resist_value = getattr(target, resist_attr, 0)
                    if random.randint(1, 100) <= (self.base_apply_chance - resist_value):
                        new_effect = copy.deepcopy(self.status_effect)
                        if self.ov_dmg is not None: new_effect.dmg_per_turn = self.ov_dmg
                        if self.ov_dur is not None: new_effect.duration = self.ov_dur
                        new_effect.on_apply(target)
                        target.active_effects.append(new_effect)
                        if self.hit_count > 1: typ(f"  -> {new_effect.name} manifestiert!")

            else:
                if self.hit_count > 1: typ("  -> Ein Strahl verpufft!")
                if self.break_on_miss: break

        # --- 3. FEEDBACK ---
        if hits > 0:
            if self.hit_count > 1:
                typ(f"\n>> {self.name}! {hits} Treffer verursachen {total_dmg} Magieschaden und {total_stance_dmg} Stance-Schaden.")
            else:
                # Originalgetreues Feedback für Einzel-Hits
                typ(f"\n>> {self.name}! {total_dmg} Magieschaden. {target.name} verliert {total_stance_dmg} Stance.")
            return True
        else:
            typ(f"\n>> {self.name} verpufft!"); return False
    
arcane_shard = SpellAbility(
    name ="Arkaner Splitter",
    tohitmod= 1.2,
    base_dmg= 5,
    wis_scaling= 0.2,
    flat_var= 1,
    flat_stance= 5,
    charges= 8
    )

############################################################################################################################

class MonsterAbility(Ability):
    def __init__(self, name, tohit_mod=1.0, hit_count=1, dmg_var_minus=0, dmg_var_plus=0, 
                 dmg_mult=1.0, category='offensive', description="greift an.", 
                 status_effect=None, ov_dmg=None, ov_dur=None, base_apply_chance=100, 
                 apply_to_self=False, is_attack=True, break_on_miss=False): 
        
        super().__init__(name, tohit_mod, hit_count=hit_count, apply_to_self=apply_to_self, 
                         is_attack=is_attack, break_on_miss=break_on_miss)
        
        self.dmg_var_minus = dmg_var_minus
        self.dmg_var_plus = dmg_var_plus
        self.dmg_mult = dmg_mult
        self.category = category
        self.description = description
        self.status_effect = status_effect
        self.ov_dmg = ov_dmg
        self.ov_dur = ov_dur
        self.base_apply_chance = base_apply_chance

    def resolve(self, user, target, weapon=None):
        # --- SONDERFALL: REINER BUFF / HEAL ---
        if not self.is_attack:
            if self.status_effect:
                new_effect = copy.deepcopy(self.status_effect)
                if self.ov_dmg is not None: new_effect.dmg_per_turn = self.ov_dmg
                if self.ov_dur is not None: new_effect.duration = self.ov_dur
                
                new_effect.on_apply(user)
                user.active_effects.append(new_effect)
                typ(f"\n{user.name} {self.description} ({new_effect.name})")
            return True

        # --- REGULÄRER ANGRIFF ---
        total_damage = 0
        hits_landed = 0

        for i in range(self.hit_count):
            hit_chance = int(user.tohitchance * self.tohitmod) - target.dodge
            
            # Treffer
            if random.randint(1, 100) <= hit_chance:
                bonus = random.randint(self.dmg_var_minus, self.dmg_var_plus)
                final_dmg = max(int((user.damage + bonus) * self.dmg_mult) - max(target.defence, 0), 1)
                
                target.hp -= final_dmg
                total_damage += final_dmg
                hits_landed += 1
                
                if self.hit_count > 1:
                    typ(f"  -> Schlag {i+1} trifft für {final_dmg} Schaden!")

                # STATUS PRO TREFFER
                if self.status_effect:
                    resist_attr = f"{self.status_effect.effect_type}_resist"
                    resist_value = getattr(target, resist_attr, 0) 
                    final_apply_chance = self.base_apply_chance - resist_value
                    
                    if self.apply_to_self or random.randint(1, 100) <= final_apply_chance:
                        new_effect = copy.deepcopy(self.status_effect)
                        if self.ov_dmg is not None: new_effect.dmg_per_turn = self.ov_dmg
                        if self.ov_dur is not None: new_effect.duration = self.ov_dur
                        
                        apply_target = user if self.apply_to_self else target
                        new_effect.on_apply(apply_target)
                        apply_target.active_effects.append(new_effect)
                        if self.hit_count > 1: typ(f"  -> {new_effect.name} appliziert!")

            # Fehlschlag
            else:
                if self.hit_count > 1:
                    typ(f"  -> Schlag {i+1} geht daneben!")
                
                # COMBO BREAKER CHECK
                if self.break_on_miss:
                    if self.hit_count > 1: typ("  -> Die Angriffsserie des Monsters reißt ab!")
                    break

        # Auswertung
        if hits_landed > 0:
            if self.hit_count == 1:
                typ(f"!! {user.name} trifft dich für {total_damage} Schaden !!")
            else:
                typ(f"!! {user.name} landet {hits_landed} Treffer für insgesamt {total_damage} Schaden !!")
            return True
        else:
            typ(f"\nDu weichst {user.name} komplett aus.")
            return False

basic_monster_attack = MonsterAbility(
    name="Einfacher Angriff",
    tohit_mod=1.0,
    hit_count=3,
    dmg_var_minus= -1,
    dmg_var_plus= 0,
    dmg_mult=0.3,
    category = "offensive",
    description="greift an."

)

quick_claws = MonsterAbility(
    name="Flinker Klauenhieb",
    tohit_mod=1.05,
    dmg_var_minus= -1,
    dmg_var_plus= 0,
    category="tactician",
    description="trifft dich mit flinken Klauen.",
    status_effect=template_bleeding_claws,
    ov_dmg=1,
    ov_dur=2,
    base_apply_chance=50
)

raging_claw = MonsterAbility(
    name="Rasender Hieb",
    tohit_mod=1.0,
    dmg_var_minus= -1,
    dmg_var_plus= 1,
    dmg_mult=1.0,
    category = "offensive",
    description="schlägt kräftig zu."

)

retreating_jab = MonsterAbility(
    name="Vorsichtiger Hieb",
    tohit_mod=1.05,
    dmg_var_minus= -1,
    dmg_var_plus= 0,
    dmg_mult=0.8,
    category="tactician",
    description="greift rasch an und zieht sich zurück.",
    status_effect=retreat_buff,
    ov_dmg=0,
    ov_dur=1,
    apply_to_self=True, # Das ist der neue Schalter!
)

tar_ooze_attack = MonsterAbility(
    name="Teermasse",
    tohit_mod=0.9,
    dmg_var_minus= -1,
    dmg_var_plus= 0,
    dmg_mult=1.0,
    category="tactician", 
    description="übergießt dich mit ätzendem Teer.",
    status_effect=template_tar,
    ov_dmg=2,          # Macht mehr Schaden als das Template
    ov_dur=2,          # Hält länger als das Template
    base_apply_chance=100 # Versucht zu 100% zu treffen (minus Hero Resist)
)


###################################################################################################
# class Item:
#     def __init__(self, name, healing_power):
#         self.name = name
#         self.healing_power = healing_power


# potion = Item (
#     name = "Kleiner Heiltrank",
#      healing_power= 8
# )

###################################################################################################

class Monster:
    def __init__(self, name, hp, maxstance, stance, ini, defence, tohitchance, dodge, damage, bleedresist, blightresist, magicresist, fireresist, lightresist, darkresist, spawntext, attacktext, hittext, misstext, deathtext, wintext, brokentext, abilities):
        self.name = name
        self.hp = hp
        self.maxstance = maxstance
        self.stance = stance
        self.ini = ini
        self.defence = defence
        self.tohitchance = tohitchance
        self.dodge = dodge
        self.damage = damage

        self.bleedresist = bleedresist
        self.blightresist = blightresist
        self.magicresist = magicresist
        self.fireresist = fireresist
        self.lightresist = lightresist
        self.darkresist = darkresist

    ###### Flavor

        self.spawntext = spawntext
        self.attacktext = attacktext
        self.hittext = hittext
        self.misstext = misstext
        self.deathtext = deathtext
        self.wintext = wintext
        self.brokentext = brokentext

        self.abilities = abilities
        self.active_effects = []

    def __str__(self):       
            return f"\n|| {self.name} ||\n|| HP: {self.hp}  INI: {self.ini}  Dodge: {self.dodge}  ToHIT: {self.tohitchance} ||\n|| DODGE: {self.dodge}  Def: {self.defence}  Damage: {self.damage} ||"

shaggy_beast = Monster (
    name = 'Haarige Bestie',
    hp = 12,
    maxstance = 16,
    stance = 16,
    ini = 12,
    defence = 0,
    tohitchance = 75,
    dodge = 0,
    damage = 3,

    bleedresist= 5,
    blightresist= 0,
    magicresist= 0,
    fireresist= -5,
    lightresist= -10,
    darkresist= 10,
    
    spawntext= "Eine abscheuliche Kreatur kriecht aus den Schatten hervor, mach dich bereit für den Kampf.",
    attacktext= "Die Bestie greift dich an!",
    hittext="",
    misstext="",
    deathtext="Du bist Gefallen, an diesem vergessenem Ort, verlassen von den Göttern, niemand wird sich an dich erinnern.",
    wintext="Sieg. Die haarige Bestie ist gefallen.",
    brokentext="",

    abilities = [basic_monster_attack]

)

lunatic_beast = Monster (
    name = 'Irrsinn',
    hp = 18,
    maxstance = 18,
    stance = 18,
    ini = 10,
    defence = 0,
    tohitchance = 65,
    dodge = 0,
    damage = 5,

    bleedresist= 5,
    blightresist= 10,
    magicresist= -5,
    fireresist= -5,
    lightresist= -10,
    darkresist= 12,
    
    spawntext= "Eine humanoid anmutende Kreatur, nackt und bedeckt mit spärlichem Fell tritt hervor. Das Monstrum keucht voller extase und wetzt seine Krallen.",
    attacktext= "Das Monstrum greift dich an!",
    hittext="",
    misstext="",
    deathtext="Die Krallen durchbohren deinen Körper. Vielleicht kriegst du noch mit wie dein Schlächter dich erratisch gegen den Boden schmettert und Speichel auf deinen Körper tropft. Du bist gefallen.",
    wintext="Das Monstrum kreischt grässlich als es zu Boden geht. Du hast gesiegt.",
    brokentext="",
    
    abilities = [basic_monster_attack]
)

undead_guard = Monster (
    name = 'Untoter Wachmann',
    hp = 15,
    maxstance = 30,
    stance = 30,
    ini = 6,
    defence = 1,
    tohitchance = 60,
    dodge = -5,
    damage = 6,

    bleedresist= 5,
    blightresist= 10,
    magicresist= 5,
    fireresist= -10,
    lightresist= -10,
    darkresist= 25,

    spawntext= "Ein bleicher Wachmann mit vergilbtem Wappenrock tritt hervor. Selbst im Tod wacht der arme Bastard über diesen Ort. Der Tote stapft leeren Blickes auf dich zu, die Waffe bereit, geführt von rasloser, kalter Mordlust.",
    attacktext= "Das Monstrum greift dich an!",
    hittext="",
    misstext="",
    deathtext="Erschlagen vom wandelnden Tod höchst selbst, der Tod gesellt sich zm Tod. Du bist gefallen.",
    wintext="Du hast gesiegt. Die untote Bestie kann nun ruhen.",
    brokentext="",
    
    abilities = [basic_monster_attack]
)

taar_monster = Monster (
    name = 'Lebender Schleim',
    hp = 25,
    maxstance = 500,
    stance = 500,
    ini = 1,
    defence = 1,
    tohitchance = 63,
    dodge = -15,
    damage = 2,

    bleedresist= 500,
    blightresist= 15,
    magicresist= -5,
    fireresist= -50,
    lightresist= 0,
    darkresist= 10,

    spawntext= "Schlurfend kriecht das Ungeheuer auf dich zu, ein zäher Haufen, schwarzer Schleim. Aus dem inneren ragen die Reste, vergangener Opfer.",
    attacktext= "Das Ungeheuer greift dich an!",
    hittext="",
    misstext="",
    deathtext="Es ist vorbei. Der schwarze Teer verschlingt deinen Körper, deine letzten Atemzüge werden von der dicken Masse verschluckt. Du bist gefallen.",
    wintext="Sieg. Endlich hällt es inne. Sein Inneres, Knochen, rostiges Metall, und andere modrige Materalien verteilen sich auf dem Boden.",
    brokentext="",

    abilities = [tar_ooze_attack]
)

################################# Encounter Listen #####################################

dungeon_encounters = [shaggy_beast, lunatic_beast, undead_guard, taar_monster]
#[shaggy_beast, lunatic_beast, undead_guard, taar_monster]

#######################################################################################################
###############################################  TEMPLATE LISTEN FÜR1
#  ROOMS #######################
# 

dungeontemplates = [
     {'name': 'Verlassene Zelle\n', 'flavor': 'Verrottetes Stroh, ein Eimer mit einer dicken Flüssigkeit gefüllt und von der Wand hängen rostige Ketten.'},
     {'name': 'Alte Speisekammer\n', 'flavor': 'Hier haben eins die Bediensteten gespeist, es riecht modrig, auf verfärbten Holztischen liegen rostiges Geschirr und geschwärzte Knochen.'},
     {'name': 'Einsamer Gang\n', 'flavor': 'Ein langer Flur, das Gemäuer wirkt alt, von den Wänden hängen zerissene Flagen und leere Fackelhalfter. Wer weiss welche Seelen hier ihren letzten Gang angetreten sind.'},
     {'name': 'Vergessener Speicher\n', 'flavor': 'Ein Lager, zumindest war es das einst, der Inhalt der Fässer schon längst verdorben, die Kisten geplündert, selbst die Spinnenweben an der Decke sind Verlassen.'},
     {'name': 'Folterkammer\n', 'flavor': 'Hier finden sich Folterwerkzeuge, manche davon als solche erkenntlich, andere ganz und gar fremdartig sorgfältig angeordnet auf Tischen und Komoden. In einer Ecke siehst du Tücher mit dunklen Flecken, und hier und dort auch Gebeine.\nEinst war dies ein Laboratorium der Schmerzen.'},
     {'name': 'Kerkercuisne\n', 'flavor': 'Hier wurden einst die Speisen für die Gefangenen zubereitet. Auf der Arbeitfläche feuchte Klumpen und die vertrockneten Überreste von Insekten und Maden, in einigen Kesseln und Töpfen befindet sich stinkender schwarzer Schleim.'},
     {'name': 'Wachbarrake\n', 'flavor': 'Ein par Hochbetten und Kommoden, auf dem Boden liegt glitschiges braunes Stroh. Die Wandbehänge haben ihre Farben verloren, was sie einst darstellten ist nicht mehr zu erkennen.'},
     {'name': 'Verborgener Schrein\n', 'flavor': 'Hier wurde ein provisorischer Schrein aufgestellt. Dieser Ort wirkt hier fehl am Platz, er passt nicht zum Rest des Verlieses.'},
     {'name': 'Latrine\n', 'flavor': 'Ein Raum den früher die Wachleute oder Gefangenen zum Waschen und verüben ihres Geschäfts genutzt haben. An einer Wand gibt es Löcher im Boden und drumrum sind die Fliesen dunkel verfärbt.\nGegenüber davon finden sich Spülbecken, Eimer und geschwärzte Tücher. Kein schöner Anblick.'}
]

dungeonsafehubtemplates = [
     {'name': 'Kapelle im Verlies\n', 
      'flavor': 'Wer weiß schon, wozu die Kapelle einst diente, jetzt ist sie ein Hoffnungsschimmer an diesem unheiligen Ort, du fühlst dich sicher und kannst Rasten.'},
     {'name': 'Verlassener Wachposten\n', 
      'flavor': 'Schreibtische, Komoden, Dokumente, und starke Türen die sich von innen verschließen lassen, es ist Zeit eine Rast einzulegen.'}
]

####################### HIER WEITER MACHEN

cavetemplates = [
     {'name': 'Offener Korridor\n', 'flavor': 'Ein langer, weiter Gang tiefer in die Höhle, auf den Wänden glitzert Feuchtigkeit.'},
     {'name': 'Gewundener Tunnel\n', 'flavor': 'Einer von vielen Korridoren in diesen Tunnelsystemen, geprägt von Stalakniten und Stalaktiten.'},
     {'name': 'Vergessene Kaverne\n', 'flavor': 'In diesem Raum gibt es Spuren von menschlicher Hand, die lange verlassenen Reste eines Unterschlupfs sind zu erkennen.'},
     {'name': 'Entlegene Grotte\n', 'flavor': 'Ein kleiner Höhlenraum mit Quellbecken. Von den Stalakniten an der Decke tropft es gemächlich und klangvoll in das Wasser.'},
     {'name': 'Kammer mit Höhlenmalereienl\n', 'flavor': 'Eigentlich eine Höhle wie viele andere, aber an den Wänden finden sich fremdartige Malereien.'},
     {'name': 'Unterirdischer Garten\n', 'flavor': 'Ein seltsamer Anblick, eine Kaverne voll mit Moos, Pilzen, Kräutern und wucherndem Efeu.'},
     {'name': 'Tempelhort\n', 'flavor': 'Ein Kruder Tempel, zusammengesetzt aus Felsplatten und Brocken, bemalt mit andersweltlichen Runen.'},
     {'name': 'Gang am Abyss\n', 'flavor': 'Ein begehbarer Pfad am Rande einer Schlucht. Sowohl die tiefen des Abgrunds als auch die andere Seite der Höhle werden von einer tiefen Schwärze verschlungen.'},
     {'name': 'Bestienhort\n', 'flavor': 'Diese Kammer scheint der Zufluchtsort einer unbekannten Kreatur zu sein. Setsame Knochen, verdorbene Fleischreste und dunkle Flecken zieren den Felsboden.'},
     {'name': 'Verlassene Sieldung\n', 'flavor': 'Eine Kaverne mit einer Hand voll primitiven Hütten und einer längst erlischten Feuerstelle. Dieser Ort wurde nicht durch Menschen geschaffen.'}
]

cavesafehubtemplates = [
     {'name': 'Versteckter Hain\n', 'flavor': 'In der Mitte der kleinen Kammer steht ein Kirschbütenraum, umgeben von einer Insel auf Wiese und Blumen. Hier fühlt es sich sicher an, du solltest rasten.'}
]

class Rooms:
     def __init__(self, template, paths, encounter, inspectrange, npc = None, event = None, inspectresult = None):
          self.name = template ['name']
          self.flavor = template ['flavor']
          self.paths = random.randint (*paths)
          self.inspectrange = inspectrange        # Liste steht bereit
          self.encounter = random.choice (encounter) if encounter else None
          self.npc = random.choice (npc) if npc else None
          self.event = random.choice (event) if event else None
          self.inspectresult = None
          pass
     def inspect(self):
          if self.inspectresult is None and self.inspectrange:
               self.inspectresult = random.choice (self.inspectrange)
          return self.inspectresult

     def __str__(self):
          return f'{self.name}\n{self.flavor}\n Pfade: {self.paths}'


class Biomes:
     def __init__(self, name, flavor, roomtemplates, safehubtemplates, encounterrange, inspectrange, npcrange, eventrange, length):
          self.name = name
          self.flavor = flavor  # im Moment zB nur ein kleiner Text beim ersten betreten um das Setting zu eröffnen
          self.roomtemplates = roomtemplates # Zieht Raumdesigns aus einer Liste
          self.safehubtemplates = safehubtemplates
          self.encounterrange = encounterrange # Listen mit encounter templates, also zB was für Monster möglich sind
          self.inspectrange = inspectrange    # Liste wird hier gebunden, später erweitere ich dieses Feature
          self.npcrange = npcrange
          self.eventrange = eventrange
          self.length = length
          pass

     def generatepath(self):
          rooms = []
          pathlength = random.randint(*self.length)
          for _ in range(pathlength):
               template = random.choice(self.roomtemplates)
               room = Rooms(
                    template = template,
                    paths = (1, 2),
                    inspectrange = self.inspectrange,
                    encounter = self.encounterrange,
                    npc = self.npcrange,
                    event = self.eventrange
               )
               rooms.append(room)
          return rooms

#######################################################################################
####################################################################################### WICHTIG ÜBERARBEITEN
#######################################################################################

dungeon = Biomes ( 
    name = 'Abgelegenes Verlies',
    flavor = 'FLAVOR TEXT INITIALISIERT BEIM BETRETEN',
    roomtemplates = dungeontemplates,
    safehubtemplates = dungeonsafehubtemplates,
    encounterrange = dungeon_encounters,
    inspectrange = ['DUMMY'],#dungeoninspects,
    npcrange = ['DUMMY'],#dungeonnpcs,
    eventrange = ['DUMMY'],#dungeonevents,
    length = (4, 12)
)

cave = Biomes ( 
    name = '',
    flavor = 'FLAVOR TEXT INITIALISIERT BEIM BETRETEN',
    roomtemplates = cavetemplates,
    safehubtemplates = cavesafehubtemplates,
    encounterrange = ['DUMMY'],#dungeonencounters,
    inspectrange = ['DUMMY'],#dungeoninspects,
    npcrange = ['DUMMY'],#dungeonnpcs,
    eventrange = ['DUMMY'],#dungeonevents,
    length = (6, 10)
)


############################################################################################################################################################################

#######################################################   Übergang von Datensatz zu Gameplay Logic        ##################################################################

############################################################################################################################################################################

def pause():
    input("\n[Weiter mit Enter]")

def game_state_after_actor_turn(actor, target, event):
    """
    Prüft, ob der actor aktive Effekte hat, die bei 'event' auslösen.
    Führt die hinterlegte Fähigkeit aus und reicht die ausgerüstete Waffe sicher weiter.
    """
    for effect in actor.active_effects[:]: # Kopie der Liste zum sicheren Iterieren
        
        if getattr(effect, 'activates_ability', False) and getattr(effect, 'trigger_event', None) == event:
            if getattr(effect, 'cast_ability', None):
                
                # FIX: Wir holen die Waffe aus dem 'equipment' Dictionary!
                equipped_weapon = None
                if hasattr(actor, 'equipment'):
                    equipped_weapon = actor.equipment.get('mainarm', None)
                
                # Failsafe wie im combat loop
                if equipped_weapon is None:
                    equipped_weapon = Weapon("Fäuste", 0, 1, 1, 0.1, 0, 0)
                
                # Ein kleiner Text, damit der Spieler merkt, was gerade passiert
                typ(f"\n[!] {effect.name} löst aus!")
                
                # Die "versteckte" Fähigkeit ausführen!
                effect.cast_ability.resolve(actor, target, equipped_weapon)
                
                # Guts-Style (Einmalig) vs. Duelist-Style (Dauerhaft)
                if getattr(effect, 'consume_on_trigger', False):
                    if effect in actor.active_effects:
                        actor.active_effects.remove(effect)

def start_combat(player, monster_template):
    # Failsafe
    round = 0
    weapon = player.equipment['mainarm']
    if weapon is None:
        # Erstelle eine temporäre "Fäuste"-Waffe, damit es nicht abstürzt
        weapon = Weapon("Fäuste", 0, 1, 1, 0.1)
    # Erstellt eine frische Kopie des Gegners
    
    enemy = copy.deepcopy(monster_template)
    typ(f"\n--- KAMPF BEGINNT: {player.charname}, {player.name} vs. {enemy.name} ---")             #########################
    
    is_riposte_available = False

    while player.hp > 0 and enemy.hp > 0:
        
        round += 1
        typ(f"\n======== RUNDE {round} =========")
# --- 1. SPIELER STATUS EFFEKTE (Anfang der Spieler-Phase) ---
        for effect in player.active_effects[:]:
            is_active = effect.tick(player)
            if not is_active:
                effect.on_remove(player)
                player.active_effects.remove(effect)
        
        if player.hp <= 0: # Check ob Spieler am Gift gestorben ist
            break

        print(f"\n{player.name}: {player.hp} HP | {enemy.name}: {enemy.hp} HP (Stance: {enemy.stance})")
        
        valid_choices = {}

# 1. Dynamische Ability-Slots (1-4)
        for i in range(1, 5):
            slot_key = f'slot_{i}'
            ability = player.abilities.get(slot_key)
            
            if ability is not None:
                # HIER DIE PRÜFUNG:
                # Wir schauen, ob das Objekt das Attribut 'is_consumable' hat und ob es True ist
                if getattr(ability, 'is_consumable', False):
                    display_name = f"{ability.name} ({ability.current_charges}/{ability.max_charges})"
                else:
                    display_name = ability.name
                    
                print(f"{i}. {display_name}")
                valid_choices[str(i)] = ability     ##### oder ability_obj ?????


###########################################################################

# 2. Waffen-Spezialangriff (W) - Platzhalter für dein nächstes Feature
        # if weapon.special_ability:
        #     print(f"W. {weapon.special_ability.name}")
        #     valid_choices["w"] = weapon.special_ability

###########################################################################

# 3. Riposte (R)
        if is_riposte_available:
            print("R. KRITISCHER ANGRIFF (Riposte)")
            # Wir weisen hier direkt ein temporäres Ability-Objekt zu
            valid_choices["r"] = WeaponAbility("RIPOSTE", 20.0, 2.5, 2.5, 0)

# Eingabe
        choice = input("\nDeine Wahl: ").lower()

        # Logik-Prüfung
        if choice in valid_choices:
            ability = valid_choices[choice]
            
            # Der Controller ruft nur noch die 'use'-Methode auf.
            # Ob es ein Zauber oder ein Waffenschlag ist, entscheidet die Klasse selbst.
            hit_success = ability.use(player, enemy, weapon)

            if hit_success:
                # Check auf Stance-Break (nur wenn Gegner noch lebt)
                if enemy.stance <= 0 and enemy.hp > 0:
                    typ("\n" + "-" * 15)
                    typ("!!! DEFENSIVE DURCHBROCHEN !!!")
                    typ(f"{enemy.name} ist wehrlos und taumelt!")
                    typ("-" * 15)
                    is_riposte_available = True
            
            # Falls der Spieler nicht die Riposte genutzt hat, verfällt sie für die nächste Runde
            if choice != "r":
                is_riposte_available = False
# 5. Monster greift an (nur wenn nicht gebrochen oder tot)

        if enemy.hp > 0:
            
            if enemy.hp > 0:
            # --- STATUS EFFEKTE VERARBEITEN (Monster-Phase) ---
                for effect in enemy.active_effects[:]: # enemy statt current_actor
                    is_active = effect.tick(enemy) # enemy kriegt den Schaden/Effekt
                    
                    if not is_active:
                        effect.on_remove(enemy) 
                        enemy.active_effects.remove(effect)

            # --- Prüfen, ob das Monster am DoT gestorben ist ---
            if enemy.hp <= 0:
                continue # Springt zum Anfang der while-Schleife, die dann beendet wird
            # FALL A: Das Monster ist gebrochen (Stance <= 0)
            if enemy.stance <= 0:
                # Wir heilen die Stance hier NICHT sofort. 
                # Wir geben nur eine Nachricht aus und überspringen den Angriff.
                typ(f"\n{enemy.name} ist verwundbar.")
                
                # WICHTIG: Wenn der Spieler die Riposte NICHT nutzt (z.B. ein Item nutzt),
                # erholt sich das Monster am ENDE dieser Taumel-Runde.
                if not is_riposte_available: 
                    enemy.stance = enemy.maxstance
                    typ(f"\n{enemy.name} ist wieder kampfbereit.")
                    
            # FALL B: Das Monster ist fit und greift normal an
            else:
                typ(f"\n{enemy.attacktext}")
                # Das Monster wählt eine seiner Fähigkeiten
                active_ability = random.choice(enemy.abilities)
                # Und nutzt sie (Berechnung & Print passieren in der resolve-Methode)
                active_ability.use(enemy, player, None)
                game_state_after_actor_turn(player, enemy, "after_enemy")

    if enemy.hp <= 0:
        typ(f"\n{enemy.wintext}")
        player.monsterkills += 1


################################################################################# Journal / Chronik ################################################################

def log_death (player, cause= "Unbekannt"):
    with open ("gefallene_helden.txt", "a", encoding="utf8") as f:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {player.charname}, {player.name} ist gefallen. Räume überlebt: {player.roomscompleted}, Gegner besiegt:{player.monsterkills}, Gold: {player.gold}, Ursache: {cause}\n")
    typ(f"\n[Chronik] Die Taten von {player.name} wurden im Journal der Gefallenen verewigt.")

####################################################################################################################################################################

def main_menu():
    print(f"\n--- WELCOME TO DRAFT {version} ---\n")
    print("1. Start Adventure")
    print("2. Character Info")
    print("3. Exit\n")
    
    choice = input("> ")
    if choice == "1":
        # Untermenü für die Charakterwahl
        print("\n--- WÄHLE DEINEN HELDEN ---")
        print("1. Gebrochener Ritter")
        print("2. Bettlerin")
        print("3. Geistlicher")
        print("4. Jägersmann")
        print("")

        char_choice = input("> ")
        
        if char_choice == "1":
            current_hero = copy.deepcopy(hero1)
            current_hero.equipment ['mainarm'] = noobsknightsword

            current_hero.abilities['slot_1'] = swiftstrike
            current_hero.abilities['slot_2'] = heavystrike
            current_hero.abilities['slot_3'] = colossal_counter

        elif char_choice == "2":
            current_hero = copy.deepcopy(hero2)
            current_hero.equipment ['mainarm'] = witcheschoice

            current_hero.abilities['slot_1'] = swiftstrike
            current_hero.abilities['slot_2'] = heavystrike
            current_hero.abilities['slot_3'] = arcane_shard

        elif char_choice == "3":
            current_hero = copy.deepcopy(hero3)
            current_hero.equipment ['mainarm'] = woodflail

            current_hero.abilities['slot_1'] = swiftstrike
            current_hero.abilities['slot_2'] = heavystrike
            current_hero.abilities['slot_3'] = pound

        elif char_choice == "4":
            current_hero = copy.deepcopy(hero4)
            current_hero.equipment ['mainarm'] = noobhuntersaxe

            current_hero.abilities['slot_1'] = swiftstrike
            current_hero.abilities['slot_2'] = heavystrike
            current_hero.abilities['slot_3'] = dividingstrike


        else:
            print("Ungültige Wahl, der Ritter tritt vor...")
            current_hero = copy.deepcopy(hero1)
            current_hero.equipment ['mainarm'] = noobsknightsword

            current_hero.abilities['slot_1'] = swiftstrike
            current_hero.abilities['slot_2'] = heavystrike
            current_hero.abilities['slot_3'] = ballancedstrike
            
        typ(f"\nDu hast {current_hero.name} gewählt...")

        print("\nWie lautet dein Name, Reisender?")
        player_charname = input("> ")
        
        if player_charname.strip():
            current_hero.charname = player_charname
        else:
            current_hero.charname = "Namenloser"
        
        typ("...\n...")
        typ("Du erwachst auf dem kalten und harten Boden einer verwahrlosten Zelle, es ist dunkel und still.")
        typ("Du solltest aufstehen und die Zelle verlassen, wer weiß was in diesen Ruinen lauert.")
        pause()
        run_dungeon(current_hero, dungeon)

    elif choice == "2":
        print("\n--- CHARAKTER ÜBERSICHT ---")
        print(hero1)
        print(hero2)
        print(hero3)
        print(hero4)
        main_menu()

def open_inventory(player):
    if not player.inventory:
        typ("\n[Inventar] Deine Taschen sind leer.")
        return

    typ("\n--- DEIN INVENTAR ---")
    # enumerate gibt uns die Nummer (i) und das Objekt (item)
    for i, item in enumerate(player.inventory):
        print(f"{i+1}. {item.name} (+{item.healing_power} HP)")
    print("0. Zurück")

    choice = input("\nWas möchtest du benutzen? (Nummer) ")
    
    if choice.isdigit():
        idx = int(choice) - 1
        
        # Prüfen, ob die gewählte Nummer im Inventar existiert
        if 0 <= idx < len(player.inventory):
            selected_item = player.inventory.pop(idx) # Item aus Liste nehmen
            
            # Heilung berechnen (max_hp ist der Deckel)
            player.hp = min(player.max_hp, player.hp + selected_item.healing_power)
            
            typ(f"\nDu benutzt {selected_item.name}.")
            typ(f"HP jetzt: {player.hp}/{player.max_hp}")
        
        elif choice == "0":
            return # Zurück zum Dungeon

###########################################################################################################################################################

def render_safe_hub(player, biome):
    # Wähle ein zufälliges Hub-Template aus dem Biom
    template = random.choice(biome.safehubtemplates)
    
    typ("\n" + "="*50)
    typ(f"*** SICHERER ORT: {template['name']} ***")
    typ(template['flavor'])
    typ("="*50)
    player.roomscompleted += 1

    # Kleine Belohnung für das Überleben des Abschnitts
    regen = int(player.max_hp * 0.3) # 30% Heilung
    player.hp = min(player.max_hp, player.hp + regen)
    typ(f"\nDurch die Rast regenerierst du {regen} HP. Aktuell: {player.hp}/{player.max_hp}")

    while True:
        print("\n--- RASTPLATZ-MENÜ ---")
        print("1. Inventar & Heilung")
        print("2. Charakterwerte prüfen")
        print("3. Tiefer in den Dungeon (Nächster Abschnitt)")
        
        choice = input("\nWas tust du? ").lower()
        if choice == "1":
            open_inventory(player)
        elif choice == "2":
            print(player)
        elif choice == "3":
            typ("\nDu löschst das Feuer und bereitest dich auf den nächsten Abschnitt vor...")
            break

###############################################################################################################################################################

def run_dungeon(player, biome):
    # Wir legen fest, dass ein Run aus 2 bis 3 Abschnitten besteht
    total_segments = random.randint(2, 3)
    
    typ(f"\n>>> Du betrittst: {biome.name} <<<")
    typ(biome.flavor)
    
    # ÄUẞERE SCHLEIFE: Die Abschnitte (Segmente)
    for segment in range(1, total_segments + 1):
        # Generiert für JEDEN Abschnitt einen eigenen Pfad
        path = biome.generatepath()
        
#########        typ(f"\n************************************************")
#########        typ(f"   ABSCHNITT {segment} von {total_segments} beginnt!")
#########        typ(f"************************************************\n")
        
# INNERE SCHLEIFE: Deine bestehende Raum-Logik
        for i, room in enumerate(path):
            typ(f"\n--- Raum {i+1}: {room.name} ---")
            typ(room.flavor)
            
            # Würfel für das Raum-Event (1-100)
            event_roll = random.randint(1, 100)
            
            # --- 40% Chance: MONSTER ---
            if event_roll <= 40:
                if biome.encounterrange:
                    monster_template = random.choice(biome.encounterrange)
                    enemy_to_fight = copy.deepcopy(monster_template)
                else:
                    enemy_to_fight = copy.deepcopy(shaggy_beast)
                    
                typ(f"\n{enemy_to_fight.spawntext}\n\n{enemy_to_fight.name}")
                start_combat(player, enemy_to_fight)
                
                if player.hp <= 0:
                    typ(f"\n{enemy_to_fight.deathtext}")
                    log_death(player, f"Erschlagen von {enemy_to_fight.name}")
                    return 

            # --- KEIN KAMPF: Out-of-Combat Ticks! ---
            else:
                # Bevor wir den Raum untersuchen, ticken die Statuseffekte
                if player.active_effects:
                    typ("\n[Status] Die Zeit vergeht...")
                    for effect in player.active_effects[:]:
                        if not effect.tick(player):
                            effect.on_remove(player)
                            player.active_effects.remove(effect)
                    
                    # Falls das Gift dich außerhalb eines Kampfes tötet
                    if player.hp <= 0:
                        typ("\nDu erliegst deinen Verletzungen in der Dunkelheit...")
                        log_death(player, "Erlag Status-Effekten außerhalb des Kampfes")
                        return

                # --- 20% Chance: FALLE ---
                if event_roll <= 60:
                    typ("\nEtwas fühlt sich falsch an... du hältst inne.")
                    if random.randint(1, 20) + (player.perception // 2) >= 15:
                        typ(f"ERFOLG! Dein scharfer Blick ({player.perception}) rettet dich.")
                        typ("Du bemerkst die gespannte Schnur am Boden und steigst vorsichtig darüber hinweg.")
                    else:
                        damage = random.randint(3, 6)
                        player.hp -= damage
                        typ(f"KLICK! Eine Armbrust löst aus der Wand aus! {damage} Schaden!")
                        typ(f"HP übrig: {player.hp}")
                        if player.hp <= 0:
                            typ("Ein falscher Schritt und ein Leben ist vorbei.")
                            log_death(player, "Einer Falle zum Opfer gefallen")
                            return

                # --- 20% Chance: LOOT ---
                elif event_roll <= 80:
                    typ("\nIn einer Ecke glitzert etwas zwischen alten Trümmern.")
                    choice = input("\nWillst du [U]ntersuchen oder [W]eitergehen? ").lower()
                    if choice == "u":
                        if random.randint(1, 100) <= 40:
                            """player.inventory.append(potion)
                            typ(f"Ein {potion.name}! Du verstaust ihn vorsichtig in deiner Tasche.")"""
                            gold_found = random.randint(20, 60)
                            player.gold += gold_found
                            typ(f"Du findest {gold_found} Goldstücke!")
                        else:
                            gold_found = random.randint(20, 60)
                            player.gold += gold_found
                            typ(f"Du findest {gold_found} Goldstücke!")
                    else:
                        typ("Du entscheidest, dass es den Lärm nicht wert ist.")

                # --- 20% Chance: NUR FLAVOR ---
                else:
                    typ("\nStille. Hier gibt es nichts zu sehen.")

            # --- ENDE DES RAUMS: INVENTAR ODER WEITER ---
            # ... (Hier geht dein Inventar-Check weiter wie bisher)

            # --- ENDE DES RAUMS: INVENTAR ODER WEITER ---
            if player.hp > 0:
                player.roomscompleted += 1
                # Wir fragen immer nach dem Inventar, außer es war der letzte Raum im letzten Segment
                if not (segment == total_segments and i == len(path) - 1):
                    while True:
                        choice = input("\n[Enter] Weiter | [I]nventar: ").lower()
                        if choice == "i":
                            open_inventory(player)
                        else:
                            break

        # --- ABSCHNITT ENDE: Sicherer Raum (außer nach dem letzten Segment) ---
        if player.hp > 0 and segment < total_segments:
            render_safe_hub(player, biome)

    # --- DUNGEON ENDE ---
    if player.hp > 0:
        typ(f"\n*** Du hast den Ausgang von {biome.name} erreicht! ***")
        if hasattr(player, 'gold'):
            typ(f"Du kehrst mit {player.gold} Goldstücken zurück.")

if __name__ == "__main__":
    main_menu()
