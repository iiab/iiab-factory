## Modifying ZIM Files

#### The Larger Picture
* Kiwix scrapes many useful sources, but sometimes the chunks are too big for IIAB.
* Using the zimdump program, the highly compressed ZIM files can be flattened into a file tree, modified, and then re-packaged as a ZIM file.
* This Notebook has a collection of tools which help in the above process.


#### How to Use this notebook
* There are install steps that only need to happen once. The cells containing these steps are set to "Raw" in the right most dropdown so that they do not execute automatically each time the notebook starts.
* The following bash script successfully installed zimtools on Ubuntu 20.04.It only needs to be run once. I think it's easier to do it from the command line, with tab completion. In a terminal, do the following:

```
cd /opt/iiab/iiab-factory/content/kiwix/generic/ 
sudo ./install-zim-tools.sh
```

* **Some conventions**: Jupyter does not want to run as root. We will create a file structure that exists in the users home directory -- so the application will be able to write all the files it needs to function.
```
<home directory>
├── new_zim
├── tree
└── working
```
In general terms, this program will dump the zim data into "tree", modify it, gather additional data into "working"
, and create a ZIM file in "new_zim"
* For testing purposes, the user will need to link from the server's document root to her home directory (so that the nginx http server in IIAB will serve the candidate in "tree):

```
cd
mkdir -p zimtest
ln -s /home/<user name>/zimtest /library/www/html/zimtest 
```


#### Installation Notes to myself
* Installing on Windows 10 insider preview WSL2. Used https://towardsdatascience.com/configuring-jupyter-notebook-in-windows-subsystem-linux-wsl2-c757893e9d69.
* First tried installing miniconda, and then installing jupyterlab with it.
* Wanted VIM bindings to edit cells, but jupyterlab version insralled by conda was too old for jupyter-vim extenion. Wound up deleting old version with conda, and used pip to install both.
* Jupyterlab seems to make the current directory its root. I created a notebook directory, and aways start jupyter lab from my home directiry
* Discovered that I could enable writing by non-root group in the iiab-factory repo, and continue to use git for version control. Needed to make symbolic link from ~/miniconda to iiab-factory.
* Reminder: Start jupyterlav in console via "jupyter lab --no-browser", and then pasteing the html link displayed into my browser.

#### Declare input and output
* The ZIM file names tend to be long and hard to remember. The PROJECT_NAME, initialized below, is used to create path names. All of the output of the zimdump program is placed in \<home\>/zimtest/\<PROJECT_NAME\>/tree. All if the intermediate downloads, and data, are placed in \<home\>/zimtest/\<PROJECT_NAME\>/working. If you use the IIAB Admin Console to download ZIMS, you will find them in /library/zims/content/.


```python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os,sys
import json
import youtube_dl
import pprint as pprint

# Declare a short project name (ZIM files are often long strings
PROJECT_NAME = 'teded'
# Input the full path of the downloaded ZIM file
ZIM_PATH = '/home/ghunt/zimtest/teded/zim-src/teded_en_all_2020-06.zim'

# The rest of the paths are computed and represent the standard layout
# Jupyter sets a working director as part of it's setup. We need it's value
HOME = os.environ['HOME']
WORKING_DIR = HOME + '/zimtest/' + PROJECT_NAME + '/working'
PROJECT_DIR = HOME + '/zimtest/' + PROJECT_NAME + '/tree'
dir_list = ['new-zim','tree','working/video_json']
for f in dir_list: 
    if not os.path.isdir(HOME + '/zimtest/' + PROJECT_NAME +'/' + f):
       os.makedirs(HOME + '/zimtest/' + PROJECT_NAME +'/' + f)

# abort if the input file cannot be found
if not os.path.exists(ZIM_PATH):
    print('%s path not found. Quitting. . .'%ZIM_PATH)
    exit

```


```python
# First we need to get a current copy of the script
dest = HOME + '/zimtest'
%cp /opt/iiab/iiab-factory/content/kiwix/de-namespace.sh {dest} 
```


```python
# The following command will zimdump to the "tree" directory
#   and remove the namespace directories
# It will return without doing anything if the "tree' is not empty
progname = HOME + '/zimtest/de-namespace.sh'
!{progname} {ZIM_PATH} {PROJECT_NAME}
```

    + set -e
    + '[' 2 -lt 2 ']'
    + '[' '!' -f /home/ghunt/zimtest/teded/zim-src/teded_en_all_2020-06.zim ']'
    ++ ls /home/ghunt/zimtest/teded/tree
    ++ wc -l
    + contents=1742
    + '[' 1742 -ne 0 ']'
    + echo 'The /home/ghunt/zimtest/teded/tree is not empty. Delete if you want to repeat this step.'
    The /home/ghunt/zimtest/teded/tree is not empty. Delete if you want to repeat this step.
    + exit 0


* The next step is a manual one that you will need to do with your browser. That is: to verify that after the namespace directories were removed, and all of the html links have been adjusted correctly. Point your browser to <hostname>/zimtest/\<PROJECT_NAME\>/tree.
* If everything is working, it's time to go fetch the information about each video from youtube.


```python

```


```python
ydl = youtube_dl.YoutubeDL()

downloaded = 0
skipped = 0
# Create a list of youtube id's
yt_id_list = os.listdir(PROJECT_DIR + '/videos/')
for yt_id in iter(yt_id_list):
    if os.path.exists(WORKING_DIR + '/video_json/' + yt_id + '.json'):
        # skip over items that are already downloadd
        skipped += 1
        continue
    with ydl:
       result = ydl.extract_info(
                'http://www.youtube.com/watch?v=%s'%yt_id,
                download=False # We just want to extract the info
                )
       downloaded += 1

    with open(WORKING_DIR + '/video_json/' + yt_id + '.json','w') as fp:
        fp.write(json.dumps(result))
    #pprint.pprint(result['upload_date'],result['view_count'])
print('%s skipped and %s downloaded'%(skipped,downloaded))
```


```python
def get_assets_data():
    outstr = ''
    data = {}
    with open(PROJECT_DIR + '/assets/data.js', 'r') as fp:
        while True:
            line = fp.readline()
            if not line:
                break
            if line.startswith('var'):
                if len(outstr) > 1:
                    # clip off the trailing semicolon
                    outstr = outstr[:-2]
                    try:
                        data[cat] = json.loads(outstr)
                    except Exception:
                        print('Parse error: %s'%outstr[:80])
                        exit
                cat = line[9:-4]
                outstr = '['
            else:
                outstr += line
    return data

zim_category_js = get_assets_data()

def get_zim_data(yt_id):
    rtn_dict = {}
    for cat in zim_category_js:
        for video in range(len(zim_category_js[cat])):
            if zim_category_js[cat][video]['id'] == yt_id:
                rtn_dict = zim_category_js[cat][video]
                break
        if len(rtn_dict) > 0: break
    return rtn_dict
```


```python
tot=0
for cat in zim_category_js:
    tot += len(zim_category_js[cat])
    print(cat, len(zim_category_js[cat]))
print('Number of Videos in all categories -- perhaps used more than once:%d'%tot)
```

    actions_and_reactions  48
    humans_vs_viruses  17
    the_world_of_sports  12
    a_day_in_the_life  11
    even_more_ted_ed_originals  160
    math_in_real_life  84
    moments_of_vision  12
    the_way_we_think  38
    superhero_science  7
    ted_ed_riddles_season_1  8
    love_actually  6
    the_wonders_of_earth  13
    ted_ed_weekend_student_talks  26
    everyone_has_a_story  16
    ted_ed_riddles_season_2  8
    ted_ed_riddles_season_4  9
    awesome_nature  146
    the_big_questions  42
    math_of_the_impossible  12
    the_artist_s_palette  19
    animation_basics  12
    getting_under_our_skin  151
    questions_no_one_yet_knows_the_answers_to  8
    think_like_a_coder  9
    uploads_from_ted_ed  1680
    new_ted_ed_originals  864
    exploring_the_senses  10
    hone_your_media_literacy_skills  7
    well_behaved_women_seldom_make_history  36
    student_voices_from_tedtalksed  3
    mind_matters  44
    out_of_this_world  41
    behind_the_curtain  30
    government_declassified  33
    inventions_that_shaped_history  46
    brain_discoveries  13
    reading_between_the_lines  54
    visualizing_data  11
    integrated_photonics  3
    playing_with_language  38
    mysteries_of_vernacular  26
    how_things_work  77
    can_you_solve_this_riddle  49
    the_works_of_william_shakespeare  9
    the_basics_of_quantum_mechanics  10
    cern_space_time_101  3
    ted_ed_loves_trees  8
    facing_our_ugly_history  3
    the_great_thanksgiving_car_ride  8
    understanding_genetics  12
    more_book_recommendations_from_ted_ed  37
    tedyouth_talks  41
    ted_ed_professional_development  5
    ted_ed_riddles_season_3  7
    history_vs  11
    you_are_what_you_eat  13
    our_changing_climate  29
    the_power_of_nature  6
    the_writer_s_workshop  25
    troubleshooting_the_world  86
    before_and_after_einstein  47
    more_money_more_problems  8
    ecofying_cities  10
    the_world_s_people_and_places  125
    more_ted_ed_originals  174
    making_the_invisible_visible  9
    there_s_a_poem_for_that_season_1  12
    cyber_influence_power  29
    discovering_the_deep  28
    national_teacher_day  19
    Number of Videos in all categories -- perhaps used more than once:4713



```python
import sqlite3
class Sqlite():
   def __init__(self, filename):
      self.conn = sqlite3.connect(filename)
      self.conn.row_factory = sqlite3.Row
      self.conn.text_factory = str
      self.c = self.conn.cursor()
    
   def __del__(self):
      self.conn.commit()
      self.c.close()
      del self.conn

def get_video_json(path):
    with open(path,'r') as fp:
        try:
            jsonstr = fp.read()
            #print(path)
            modules = json.loads(jsonstr.strip())
        except Exception as e:
            print(e)
            print(jsonstr[:80])
            return {}
    return modules

def video_size(yt_id):
    return os.path.getsize(PROJECT_DIR + '/videos/' + yt_id + '/video.webm')

def make_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def download_file(url,todir):
    local_filename = url.split('/')[-1]
    r = requests.get(url)
    f = open(todir + '/' + local_filename, 'wb')
    for chunk in r.iter_content(chunk_size=512 * 1024):
        if chunk:
            f.write(chunk)
    f.close()

def initialize_db():
    sql = 'CREATE TABLE IF NOT EXISTS video_info ('\
            'yt_id TEXT UNIQUE, zim_size INTEGER, view_count INTEGER, average_rating REAL,slug TEXT)'
    db.c.execute(sql)

db = Sqlite(WORKING_DIR + '/zim_video_info.sqlite')
initialize_db()
yt_id_list = os.listdir(WORKING_DIR + '/video_json/' )
for yt_id in iter(yt_id_list):
    zim_data = get_zim_data(yt_id[:-5])
    slug = zim_data['slug']
    data = get_video_json(WORKING_DIR + "/video_json/" + yt_id)
    if len(data) == 0:continue
    vsize = video_size(yt_id[:-5])
    view_count = data['view_count']
    average_rating = data['average_rating']
    sql = 'INSERT OR REPLACE INTO video_info VALUES (?,?,?,?,?)'
    db.c.execute(sql,[yt_id[:-5],vsize,view_count,average_rating,slug])
db.conn.commit()
```

    Expecting value: line 1 column 1 (char 0)
    
    Expecting value: line 1 column 1 (char 0)
    



```python

```


```python
sqlite_db = WORKING_DIR + '/zim_video_info.sqlite'
!sqlite3 {sqlite_db} '.headers on' 'select * from video_info limit 2'
```

    yt_id|zim_size|view_count|average_rating|slug
    eFCk3qWmCoo|29780783|13594|4.9529409|how_arduino_is_open_sourcing_imagination_massimo_banzi
    0Wb5obt7QO0|15978414|6924|4.9375|how_we_found_the_giant_squid_edith_widder


#### Select the cutoff using view count and total size
* Order the videos by view count. Then select the sum line in the that has the target sum.


```python
def human_readable(num):
    # return 3 significant digits and unit specifier
    num = float(num)
    units = [ '','K','M','G']
    for i in range(4):
        if num<10.0:
            return "%.2f%s"%(num,units[i])
        if num<100.0:
            return "%.1f%s"%(num,units[i])
        if num < 1000.0:
            return "%.0f%s"%(num,units[i])
        num /= 1024.0

sql = 'select slug,zim_size,view_count from video_info order by view_count desc'
tot_sum = 0
db.c.execute(sql)
rows = db.c.fetchall()
print('%60s %6s %6s %6s'%('Name','Size','Sum','Vi'
for row in rows:
    tot_sum += row['zim_size']
    print('%60s %6s %6s %6s'%(row['slug'][:60],human_readable(row['zim_size']),\
                              human_readable(tot_sum),human_readable(row['view_count']),))
```

              questions_no_one_knows_the_answers_to_full_version  34.0M  34.0M  21.4M
              can_you_solve_the_prisoner_hat_riddle_alex_gendler  6.65M  40.7M  19.6M
                        the_infinite_hotel_paradox_jeff_dekofsky  9.92M  50.6M  19.1M
         what_are_those_floaty_things_in_your_eye_michael_mauser  6.76M  57.3M  18.6M
                    can_you_solve_the_bridge_riddle_alex_gendler  6.09M  63.4M  16.6M
                               the_language_of_lying_noah_zandan  8.93M  72.4M  14.4M
                          what_makes_muscles_grow_jeffrey_siegel  6.63M  79.0M  11.9M
                      the_loathsome_lethal_mosquito_rose_eveleth  4.87M  83.9M  11.6M
    can_you_solve_the_famously_difficult_green_eyed_logic_puzzle  8.05M  91.9M  11.5M
     why_don_t_perpetual_motion_machines_ever_work_netta_schramm  16.6M   108M  11.0M
                    which_is_stronger_glue_or_tape_elizabeth_cox  12.6M   121M  10.8M
               can_you_solve_einsteins_riddle_dan_van_der_vieren  8.86M   130M  10.3M
          a_glimpse_of_teenage_life_in_ancient_rome_ray_laurence  15.9M   146M  10.1M
                        how_sugar_affects_the_brain_nicole_avena  16.5M   162M  9.83M
                          how_thor_got_his_hammer_scott_a_mellor  8.02M   170M  9.68M
                can_you_solve_the_three_gods_riddle_alex_gendler  7.41M   178M  9.52M
        what_would_happen_if_you_didnt_drink_water_mia_nacamulli  8.75M   187M  9.38M
            what_would_happen_if_you_didnt_sleep_claudia_aguirre  7.82M   194M  9.24M
                      can_you_solve_the_locker_riddle_lisa_winer  6.77M   201M  9.20M
     how_playing_an_instrument_benefits_your_brain_anita_collins  8.59M   210M  9.14M
                 the_benefits_of_a_bilingual_brain_mia_nacamulli  11.5M   221M  9.09M
             can_you_solve_the_wizard_standoff_riddle_dan_finkel  8.15M   229M  8.75M
           how_the_food_you_eat_affects_your_brain_mia_nacamulli  14.6M   244M  8.64M
                       can_you_solve_the_virus_riddle_lisa_winer  9.66M   254M  8.58M
    how_to_practice_effectively_for_just_about_anything_annie_bo  9.17M   263M  8.50M
                        why_do_cats_act_so_weird_tony_buffington  11.9M   275M  8.42M
             can_you_solve_the_prisoner_boxes_riddle_yossi_elran  9.44M   284M  8.26M
                 can_you_solve_the_temple_riddle_dennis_e_shasha  6.70M   291M  8.12M
                       four_sisters_in_ancient_rome_ray_laurence  17.2M   308M  8.04M
                      how_does_a_jellyfish_sting_neosha_s_kashef  7.51M   316M  7.97M
                    the_benefits_of_good_posture_murat_dalkilinc  5.78M   321M  7.89M
                           how_does_anesthesia_work_steven_zheng  8.05M   329M  7.82M
    the_unexpected_math_behind_van_gogh_s_starry_night_natalya_s  14.7M   344M  7.69M
             a_day_in_the_life_of_a_roman_soldier_robert_garland  9.16M   353M  7.59M
    the_atlantic_slave_trade_what_too_few_textbooks_told_you_ant  10.8M   364M  7.55M
                    can_you_solve_the_passcode_riddle_ganesh_pai  7.16M   371M  7.48M
                    can_you_solve_the_pirate_riddle_alex_gendler  9.00M   380M  7.46M
                   the_psychology_of_narcissism_w_keith_campbell  8.95M   389M  7.33M
                   the_five_major_world_religions_john_bellaimey  36.6M   426M  7.32M
                               how_do_tornadoes_form_james_spann  8.52M   434M  7.31M
                     the_myth_of_cupid_and_psyche_brendan_pelsue  16.4M   451M  7.31M
                       a_brie_f_history_of_cheese_paul_kindstedt  7.95M   459M  7.05M
                               what_makes_a_hero_matthew_winkler  11.4M   470M  6.93M
    who_were_the_vestal_virgins_and_what_was_their_job_peta_gree  12.8M   483M  6.85M
         5_tips_to_improve_your_critical_thinking_samantha_agoos  6.79M   490M  6.82M
    the_dark_ages_how_dark_were_they_really_crash_course_world_h  29.8M   519M  6.78M
                 why_are_some_people_left_handed_daniel_m_abrams  8.22M   528M  6.77M
                              what_is_depression_helen_m_farrell  7.12M   535M  6.74M
    how_did_hitler_rise_to_power_alex_gendler_and_anthony_hazard  11.7M   547M  6.73M
    what_happens_to_our_bodies_after_we_die_farnaz_khatibi_jafar  8.41M   555M  6.66M
                          3_tips_to_boost_your_confidence_ted_ed  9.28M   564M  6.66M
           can_you_solve_the_counterfeit_coin_riddle_jennifer_lu  9.45M   574M  6.66M
      why_incompetent_people_think_they_re_amazing_david_dunning  10.9M   585M  6.66M
                      can_you_solve_the_frog_riddle_derek_abbott  6.91M   591M  6.61M
                            the_myth_of_arachne_iseult_gillespie  9.15M   601M  6.46M
    does_your_vote_count_the_electoral_college_explained_christi  11.1M   612M  6.44M
                                  how_tsunamis_work_alex_gendler  8.95M   621M  6.41M
                                       just_how_small_is_an_atom  14.7M   635M  5.96M
                      why_sitting_is_bad_for_you_murat_dalkilinc  8.20M   643M  5.86M
                                       why_do_women_have_periods  7.05M   651M  5.86M
                      how_your_digestive_system_works_emma_bryce  6.85M   657M  5.85M
                how_do_cigarettes_affect_the_body_krishna_sudhir  12.7M   670M  5.85M
             why_do_we_cry_the_three_types_of_tears_alex_gendler  7.77M   678M  5.74M
      the_great_conspiracy_against_julius_caesar_kathryn_tempest  10.4M   688M  5.72M
    mansa_musa_one_of_the_wealthiest_people_who_ever_lived_jessi  12.4M   701M  5.72M
          the_rise_and_fall_of_the_berlin_wall_konrad_h_jarausch  9.52M   710M  5.70M
    the_myth_of_thor_s_journey_to_the_land_of_giants_scott_a_mel  7.63M   718M  5.69M
                     what_makes_something_kafkaesque_noah_tavlin  19.7M   737M  5.68M
         how_we_conquered_the_deadly_smallpox_virus_simona_zompi  9.12M   747M  5.66M
                     the_worlds_most_mysterious_book_stephen_bax  9.37M   756M  5.58M
                         the_myth_of_prometheus_iseult_gillespie  8.23M   764M  5.57M
                             why_can_t_you_divide_by_zero_ted_ed  7.70M   772M  5.56M
                   8_traits_of_successful_people_richard_st_john  19.1M   791M  5.49M
                      the_myth_of_icarus_and_daedalus_amy_adkins  15.2M   806M  5.47M
          the_tragic_myth_of_orpheus_and_eurydice_brendan_pelsue  7.92M   814M  5.43M
    the_myth_behind_the_chinese_zodiac_megan_campisi_and_pen_pen  6.53M   821M  5.42M
                    the_philosophy_of_stoicism_massimo_pigliucci  10.3M   831M  5.38M
                   can_you_solve_the_egg_drop_riddle_yossi_elran  8.41M   839M  5.38M
                           historys_deadliest_colors_j_v_maranto  14.5M   854M  5.36M
                     how_to_build_a_fictional_world_kate_messner  10.1M   864M  5.33M
                 the_greatest_ted_talk_ever_sold_morgan_spurlock  38.9M   903M  5.31M
    schrodinger_s_cat_a_thought_experiment_in_quantum_mechanics_  6.93M   910M  5.25M
                          where_does_gold_come_from_david_lunney  9.66M   920M  5.23M
                cell_vs_virus_a_battle_for_health_shannon_stiles  10.1M   930M  5.19M
              can_you_solve_the_river_crossing_riddle_lisa_winer  8.29M   938M  5.16M
                                      why_do_we_dream_amy_adkins  13.5M   951M  5.13M
                 can_you_solve_the_airplane_riddle_judd_a_schorr  9.30M   961M  5.09M
             the_wars_that_inspired_game_of_thrones_alex_gendler  11.0M   972M  5.07M
                     the_history_of_chocolate_deanna_pucciarelli  8.67M   980M  5.07M
    the_myth_of_king_midas_and_his_golden_touch_iseult_gillespie  16.3M   997M  5.03M
                     is_marijuana_bad_for_your_brain_anees_bahji  12.1M  0.99G  4.89M
                   cannibalism_in_the_animal_kingdom_bill_schutt  9.64M  0.99G  4.89M
                           the_science_of_attraction_dawn_maslar  6.78M  1.00G  4.88M
                                       why_do_we_itch_emma_bryce  13.6M  1.01G  4.83M
       the_three_different_ways_mammals_give_birth_kate_slabosky  8.55M  1.02G  4.77M
                            history_vs_genghis_khan_alex_gendler  10.4M  1.03G  4.77M
                       the_myth_of_pandoras_box_iseult_gillespie  10.9M  1.04G  4.73M
                    can_you_solve_the_fish_riddle_steve_wyborney  8.49M  1.05G  4.71M
    exponential_growth_how_folding_paper_can_get_you_to_the_moon  6.30M  1.06G  4.67M
    the_egyptian_book_of_the_dead_a_guidebook_for_the_underworld  7.39M  1.07G  4.62M
                    what_makes_tattoos_permanent_claudia_aguirre  8.82M  1.07G  4.61M
                               history_vs_cleopatra_alex_gendler  7.53M  1.08G  4.61M
             can_you_solve_the_control_room_riddle_dennis_shasha  6.73M  1.09G  4.58M
                     why_the_metric_system_matters_matt_anticole  7.17M  1.09G  4.51M
                         how_do_pregnancy_tests_work_tien_nguyen  8.90M  1.10G  4.51M
                               the_myth_of_sisyphus_alex_gendler  9.76M  1.11G  4.48M
    why_do_competitors_open_their_stores_next_to_one_another_jac  8.49M  1.12G  4.47M
    what_makes_the_great_wall_of_china_so_extraordinary_megan_ca  6.95M  1.13G  4.45M
                        platos_allegory_of_the_cave_alex_gendler  13.0M  1.14G  4.41M
                    if_superpowers_were_real_immortality_joy_lin  14.3M  1.15G  4.40M
    dna_hot_pockets_the_longest_word_ever_crash_course_biology_1  44.7M  1.20G  4.39M
    a_day_in_the_life_of_an_ancient_egyptian_doctor_elizabeth_co  7.03M  1.21G  4.35M
                          does_time_exist_andrew_zimmerman_jones  15.1M  1.22G  4.33M
           the_myth_of_hercules_12_labors_in_8_bits_alex_gendler  23.8M  1.24G  4.30M
                             history_s_worst_nun_theresa_a_yugar  13.6M  1.26G  4.29M
            can_you_solve_the_unstoppable_blob_riddle_dan_finkel  5.70M  1.26G  4.28M
                                    how_to_read_music_tim_hansen  8.54M  1.27G  4.28M
               what_happens_during_a_heart_attack_krishna_sudhir  8.09M  1.28G  4.26M
                           a_brief_history_of_chess_alex_gendler  9.53M  1.29G  4.26M
                                      string_theory_brian_greene  37.8M  1.32G  4.25M
    what_s_the_difference_between_accuracy_and_precision_matt_an  7.40M  1.33G  4.23M
        the_tale_of_the_doctor_who_defied_death_iseult_gillespie  9.68M  1.34G  4.23M
                          how_a_wound_heals_itself_sarthak_sinha  7.79M  1.35G  4.18M
                           how_do_solar_panels_work_richard_komp  7.14M  1.36G  4.17M
      why_the_octopus_brain_is_so_extraordinary_claudio_l_guerra  7.17M  1.36G  4.17M
                         why_elephants_never_forget_alex_gendler  8.72M  1.37G  4.16M
                   how_does_money_laundering_work_delena_d_spann  11.9M  1.38G  4.10M
                         where_did_russia_come_from_alex_gendler  13.9M  1.40G  4.06M
    why_do_animals_have_such_different_lifespans_joao_pedro_de_m  7.36M  1.40G  4.02M
                  how_stress_affects_your_brain_madhumita_murgia  7.50M  1.41G  4.00M
                                  the_history_of_tea_shunan_teng  7.57M  1.42G  3.98M
                    debunking_the_myths_of_ocd_natascha_m_santos  9.04M  1.43G  3.97M
                           what_is_dyslexia_kelli_sandman_hurley  7.51M  1.43G  3.97M
        the_chinese_myth_of_the_immortal_white_snake_shunan_teng  7.80M  1.44G  3.96M
                             why_are_sloths_so_slow_kenny_coogan  7.71M  1.45G  3.95M
             the_wacky_history_of_cell_theory_lauren_royal_woods  15.4M  1.47G  3.90M
            how_stress_affects_your_body_sharon_horesh_bergquist  8.32M  1.47G  3.85M
        can_you_solve_the_penniless_pilgrim_riddle_daniel_finkel  6.60M  1.48G  3.84M
                          how_does_asthma_work_christopher_e_gaw  8.91M  1.49G  3.83M
    meet_the_tardigrade_the_toughest_animal_on_earth_thomas_boot  7.11M  1.50G  3.82M
                          history_vs_vladimir_lenin_alex_gendler  15.9M  1.51G  3.80M
            why_do_we_love_a_philosophical_inquiry_skye_c_cleary  9.31M  1.52G  3.74M
          how_does_the_rorschach_inkblot_test_work_damion_searls  12.9M  1.53G  3.71M
     exploring_other_dimensions_alex_rosenthal_and_george_zaidan  8.57M  1.54G  3.69M
                         why_do_your_knuckles_pop_eleanor_nelsen  12.1M  1.55G  3.68M
      the_history_of_the_world_according_to_cats_eva_maria_geigl  11.9M  1.56G  3.67M
                      history_vs_napoleon_bonaparte_alex_gendler  8.85M  1.57G  3.64M
                           why_do_people_join_cults_janja_lalich  12.4M  1.59G  3.63M
         what_is_the_heisenberg_uncertainty_principle_chad_orzel  5.96M  1.59G  3.62M
                       at_what_moment_are_you_dead_randall_hayes  9.25M  1.60G  3.61M
                        how_blood_pressure_works_wilfred_manzano  8.16M  1.61G  3.59M
                       where_did_english_come_from_claire_bowern  9.49M  1.62G  3.58M
                 the_benefits_of_a_good_night_s_sleep_shai_marcu  11.3M  1.63G  3.58M
                        how_do_vitamins_work_ginnie_trinh_nguyen  9.07M  1.64G  3.55M
          how_do_carbohydrates_impact_your_health_richard_j_wood  8.69M  1.65G  3.54M
             sex_determination_more_complicated_than_you_thought  17.4M  1.66G  3.54M
    how_to_manage_your_time_more_effectively_according_to_machin  7.65M  1.67G  3.54M
                                  is_telekinesis_real_emma_bryce  8.68M  1.68G  3.54M
      would_you_sacrifice_one_person_to_save_five_eleanor_nelsen  7.06M  1.69G  3.52M
           the_treadmill_s_dark_and_twisted_past_conor_heffernan  14.6M  1.70G  3.52M
                         what_causes_kidney_stones_arash_shadman  6.68M  1.71G  3.51M
    why_is_vermeer_s_girl_with_the_pearl_earring_considered_a_ma  8.37M  1.71G  3.50M
                          the_sonic_boom_problem_katerina_kaouri  11.3M  1.73G  3.48M
       the_rise_and_fall_of_the_byzantine_empire_leonora_neville  8.15M  1.73G  3.47M
                              what_causes_cavities_mel_rosenberg  9.96M  1.74G  3.46M
                        what_is_bipolar_disorder_helen_m_farrell  8.08M  1.75G  3.44M
              the_hidden_meanings_of_yin_and_yang_john_bellaimey  13.5M  1.76G  3.43M
                                   how_to_make_a_mummy_len_bloch  7.41M  1.77G  3.43M
        how_parasites_change_their_host_s_behavior_jaap_de_roode  10.1M  1.78G  3.42M
                 how_does_the_stock_market_work_oliver_elfenbaum  9.18M  1.79G  3.41M
               the_pharaoh_that_wouldn_t_be_forgotten_kate_green  9.09M  1.80G  3.41M
    from_slave_to_rebel_gladiator_the_life_of_spartacus_fiona_ra  19.2M  1.82G  3.40M
    mary_s_room_a_philosophical_thought_experiment_eleanor_nelse  6.90M  1.82G  3.38M
               should_you_trust_unanimous_decisions_derek_abbott  6.56M  1.83G  3.37M
                         the_magic_of_vedic_math_gaurav_tekriwal  19.2M  1.85G  3.36M
                         why_is_glass_transparent_mark_miodownik  6.71M  1.86G  3.35M
                             history_vs_che_guevara_alex_gendler  11.8M  1.87G  3.35M
                        why_are_there_so_many_insects_murry_gans  7.45M  1.88G  3.34M
             the_immortal_cells_of_henrietta_lacks_robin_bulleri  9.48M  1.88G  3.34M
                             how_to_unboil_an_egg_eleanor_nelsen  7.29M  1.89G  3.34M
    how_to_stay_calm_under_pressure_noa_kageyama_and_pen_pen_che  8.06M  1.90G  3.33M
              the_scientific_origins_of_the_minotaur_matt_kaplan  10.4M  1.91G  3.31M
        the_history_of_the_cuban_missile_crisis_matthew_a_jordan  9.69M  1.92G  3.29M
                    history_vs_christopher_columbus_alex_gendler  10.0M  1.93G  3.28M
    what_really_happens_to_the_plastic_you_throw_away_emma_bryce  6.68M  1.94G  3.28M
      why_should_you_read_tolstoy_s_war_and_peace_brendan_pelsue  10.4M  1.95G  3.26M
         the_real_story_behind_archimedes_eureka_armand_d_angour  10.3M  1.96G  3.26M
                            is_time_travel_possible_colin_stuart  11.5M  1.97G  3.21M
           what_happens_when_you_remove_the_hippocampus_sam_kean  7.69M  1.97G  3.21M
                      how_to_spot_a_pyramid_scheme_stacie_bosley  7.23M  1.98G  3.20M
                            the_history_of_marriage_alex_gendler  8.24M  1.99G  3.17M
                    human_sperm_vs_the_sperm_whale_aatish_bhatia  10.1M  2.00G  3.16M
                           platos_best_and_worst_ideas_wisecrack  9.76M  2.01G  3.14M
                         is_it_bad_to_hold_your_pee_heba_shaheed  6.40M  2.02G  3.13M
    the_incredible_history_of_china_s_terracotta_warriors_megan_  7.41M  2.02G  3.13M
    why_isn_t_the_world_covered_in_poop_eleanor_slade_and_paul_m  7.34M  2.03G  3.10M
                  what_is_deja_vu_what_is_deja_vu_michael_molina  5.50M  2.03G  3.09M
                           the_science_of_spiciness_rose_eveleth  6.03M  2.04G  3.09M
    why_should_you_listen_to_vivaldi_s_four_seasons_betsy_schwar  8.74M  2.05G  3.08M
    the_cambodian_myth_of_lightning_thunder_and_rain_prumsodun_o  11.6M  2.06G  3.07M
      what_percentage_of_your_brain_do_you_use_richard_e_cytowic  8.93M  2.07G  3.05M
                      the_arctic_vs_the_antarctic_camille_seaman  6.20M  2.08G  3.05M
                  what_is_zeno_s_dichotomy_paradox_colm_kelleher  8.55M  2.08G  3.04M
                   can_you_solve_the_dark_coin_riddle_lisa_winer  9.85M  2.09G  3.00M
                    where_do_superstitions_come_from_stuart_vyse  8.38M  2.10G  3.00M
            can_you_solve_the_seven_planets_riddle_edwin_f_meyer  9.29M  2.11G  2.98M
                       how_to_write_descriptively_nalo_hopkinson  12.1M  2.12G  2.96M
                              what_causes_headaches_dan_kwartler  9.18M  2.13G  2.94M
    what_really_happened_during_the_salem_witch_trials_brian_a_p  10.1M  2.14G  2.92M
                     why_is_it_so_hard_to_cure_cancer_kyuson_yun  14.5M  2.16G  2.91M
                                            how_pandemics_spread  18.7M  2.17G  2.90M
                        how_to_recognize_a_dystopia_alex_gendler  20.0M  2.19G  2.90M
            how_the_food_you_eat_affects_your_gut_shilpa_ravella  12.3M  2.21G  2.90M
    which_is_better_soap_or_hand_sanitizer_alex_rosenthal_and_pa  14.0M  2.22G  2.90M
      can_you_solve_the_leonardo_da_vinci_riddle_tanya_khovanova  7.97M  2.23G  2.89M
    what_s_the_fastest_way_to_alphabetize_your_bookshelf_chand_j  6.22M  2.23G  2.87M
                            how_big_is_infinity_dennis_wildfogel  11.5M  2.24G  2.87M
                     how_does_caffeine_keep_us_awake_hanan_qasim  8.05M  2.25G  2.86M
                   how_to_defeat_a_dragon_with_math_garth_sundem  8.27M  2.26G  2.86M
      the_surprising_reason_our_muscles_get_tired_christian_moro  10.6M  2.27G  2.84M
                       the_true_story_of_sacajawea_karen_mensing  5.88M  2.28G  2.84M
               vampires_folklore_fantasy_and_fact_michael_molina  11.5M  2.29G  2.84M
                           history_vs_richard_nixon_alex_gendler  9.98M  2.30G  2.83M
                    how_do_animals_experience_pain_robyn_j_crook  7.80M  2.30G  2.81M
                                         when_is_a_pandemic_over  15.3M  2.32G  2.80M
              poison_vs_venom_what_s_the_difference_rose_eveleth  7.73M  2.33G  2.78M
    what_would_happen_if_every_human_suddenly_disappeared_dan_kw  9.30M  2.34G  2.77M
                                   what_is_entropy_jeff_phillips  7.75M  2.34G  2.77M
                 what_s_invisible_more_than_you_think_john_lloyd  19.8M  2.36G  2.76M
                         a_brief_history_of_alcohol_rod_phillips  8.92M  2.37G  2.76M
                   how_the_heart_actually_pumps_blood_edmond_hui  6.19M  2.38G  2.75M
                      the_power_of_the_placebo_effect_emma_bryce  8.45M  2.39G  2.75M
                                             how_far_is_a_second  2.58M  2.39G  2.75M
    this_is_sparta_fierce_warriors_of_the_ancient_world_craig_zi  8.43M  2.40G  2.75M
                         why_can_t_we_see_evidence_of_alien_life  15.4M  2.41G  2.74M
            can_you_solve_the_false_positive_riddle_alex_gendler  10.4M  2.42G  2.73M
           history_through_the_eyes_of_a_chicken_chris_a_kniesly  14.1M  2.44G  2.73M
                 how_simple_ideas_lead_to_scientific_discoveries  14.9M  2.45G  2.72M
                  einstein_s_twin_paradox_explained_amber_stuver  11.7M  2.46G  2.71M
    how_do_you_decide_where_to_go_in_a_zombie_apocalypse_david_h  5.98M  2.47G  2.70M
            football_physics_the_impossible_free_kick_erez_garty  7.58M  2.47G  2.66M
    how_high_can_you_count_on_your_fingers_spoiler_much_higher_t  9.61M  2.48G  2.63M
    are_elvish_klingon_dothraki_and_na_vi_real_languages_john_mc  8.70M  2.49G  2.62M
                    can_you_solve_the_rogue_ai_riddle_dan_finkel  9.02M  2.50G  2.62M
                     how_does_alcohol_make_you_drunk_judy_grisel  8.19M  2.51G  2.62M
    how_did_dracula_become_the_world_s_most_famous_vampire_stanl  10.5M  2.52G  2.61M
                      a_brief_history_of_cannibalism_bill_schutt  8.18M  2.53G  2.60M
    the_surprising_reason_you_feel_awful_when_you_re_sick_marco_  7.36M  2.54G  2.60M
                      what_causes_antibiotic_resistance_kevin_wu  8.13M  2.54G  2.57M
             the_fascinating_history_of_cemeteries_keith_eggener  9.83M  2.55G  2.57M
    the_most_groundbreaking_scientist_you_ve_never_heard_of_addi  6.87M  2.56G  2.56M
                    why_is_ketchup_so_hard_to_pour_george_zaidan  10.0M  2.57G  2.56M
    what_is_imposter_syndrome_and_how_can_you_combat_it_elizabet  6.54M  2.58G  2.56M
         a_day_in_the_life_of_an_ancient_athenian_robert_garland  10.1M  2.59G  2.55M
                what_gives_a_dollar_bill_its_value_doug_levinson  7.24M  2.59G  2.53M
                                   should_we_eat_bugs_emma_bryce  10.2M  2.60G  2.52M
                       the_chemistry_of_cookies_stephanie_warren  6.33M  2.61G  2.51M
                           michio_kaku_what_is_deja_vu_big_think  6.56M  2.61G  2.51M
    would_you_opt_for_a_life_with_no_pain_hayley_levitt_and_beth  6.52M  2.62G  2.50M
                              how_smart_are_dolphins_lori_marino  9.95M  2.63G  2.49M
                              a_brief_history_of_goths_dan_adams  11.8M  2.64G  2.48M
     why_doesnt_the_leaning_tower_of_pisa_fall_over_alex_gendler  9.48M  2.65G  2.45M
     the_amazing_ways_plants_defend_themselves_valentin_hammoudi  11.5M  2.66G  2.45M
    how_mendel_s_pea_plants_helped_us_understand_genetics_horten  5.11M  2.67G  2.44M
                                 how_big_is_the_ocean_scott_gass  7.83M  2.68G  2.40M
                  what_caused_the_french_revolution_tom_mullaney  13.9M  2.69G  2.40M
       the_rise_and_fall_of_the_mongol_empire_anne_f_broadbridge  12.1M  2.70G  2.39M
                       why_do_blood_types_matter_natalie_s_hodge  9.45M  2.71G  2.37M
                     how_does_your_immune_system_work_emma_bryce  9.65M  2.72G  2.37M
            can_you_solve_the_stolen_rubies_riddle_dennis_shasha  10.1M  2.73G  2.36M
                         the_genius_of_marie_curie_shohini_ghose  9.06M  2.74G  2.35M
    mating_frenzies_sperm_hoards_and_brood_raids_the_life_of_a_f  12.0M  2.75G  2.35M
               dark_matter_the_matter_we_can_t_see_james_gillies  22.0M  2.77G  2.34M
                                    what_is_a_calorie_emma_bryce  5.65M  2.78G  2.32M
               how_does_your_body_process_medicine_celine_valery  9.04M  2.79G  2.32M
    zen_koans_unsolvable_enigmas_designed_to_break_your_brain_pu  14.2M  2.80G  2.32M
                     who_am_i_a_philosophical_inquiry_amy_adkins  10.6M  2.81G  2.31M
       how_much_of_what_you_see_is_a_hallucination_elizabeth_cox  12.7M  2.82G  2.30M
                     how_do_fish_make_electricity_eleanor_nelsen  10.4M  2.83G  2.28M
                               how_languages_evolve_alex_gendler  7.30M  2.84G  2.27M
              the_rise_and_fall_of_the_inca_empire_gordon_mcewan  14.5M  2.85G  2.27M
              can_you_solve_the_giant_cat_army_riddle_dan_finkel  9.01M  2.86G  2.26M
    three_anti_social_skills_to_improve_your_writing_nadia_kalma  6.89M  2.87G  2.26M
          why_doesnt_anything_stick_to_teflon_ashwini_bharathula  8.67M  2.88G  2.26M
            the_evolution_of_animal_genitalia_menno_schilthuizen  13.2M  2.89G  2.25M
                        why_do_some_people_go_bald_sarthak_sinha  7.62M  2.90G  2.25M
    why_should_you_read_one_hundred_years_of_solitude_francisco_  14.1M  2.91G  2.23M
                    the_science_of_skin_color_angela_koine_flynn  9.01M  2.92G  2.23M
         the_physics_of_the_hardest_move_in_ballet_arleen_sugano  7.90M  2.93G  2.23M
                                how_to_understand_power_eric_liu  14.7M  2.94G  2.22M
                       the_deadly_irony_of_gunpowder_eric_rosado  8.75M  2.95G  2.22M
    should_you_trust_your_first_impression_peter_mende_siedlecki  9.92M  2.96G  2.21M
                       how_computer_memory_works_kanawat_senanan  13.2M  2.97G  2.21M
    how_one_piece_of_legislation_divided_a_nation_ben_labaree_jr  13.8M  2.99G  2.20M
       can_you_solve_the_multiplying_rabbits_riddle_alex_gendler  7.66M  3.00G  2.20M
         can_you_solve_the_buried_treasure_riddle_daniel_griller  9.47M  3.00G  2.19M
    how_a_single_celled_organism_almost_wiped_out_life_on_earth_  7.87M  3.01G  2.19M
    light_seconds_light_years_light_centuries_how_to_measure_ext  16.7M  3.03G  2.18M
             can_you_solve_the_secret_werewolf_riddle_dan_finkel  7.43M  3.04G  2.18M
    how_is_power_divided_in_the_united_states_government_belinda  5.20M  3.04G  2.17M
                               what_causes_insomnia_dan_kwartler  7.39M  3.05G  2.17M
                          how_do_you_know_you_exist_james_zucker  6.00M  3.05G  2.16M
           myths_and_misconceptions_about_evolution_alex_gendler  7.18M  3.06G  2.15M
    why_do_honeybees_love_hexagons_zack_patterson_and_andy_peter  8.57M  3.07G  2.15M
                  can_you_solve_the_jail_break_riddle_dan_finkel  7.25M  3.08G  2.14M
                     why_is_mount_everest_so_tall_michele_koppes  7.35M  3.08G  2.13M
    jellyfish_predate_dinosaurs_how_have_they_survived_so_long_d  11.0M  3.09G  2.13M
                      why_should_you_read_macbeth_brendan_pelsue  10.5M  3.10G  2.13M
           making_a_ted_ed_lesson_bringing_a_pop_up_book_to_life  15.1M  3.12G  2.12M
                            what_causes_bad_breath_mel_rosenberg  8.75M  3.13G  2.11M
                          history_vs_andrew_jackson_james_fester  7.65M  3.14G  2.11M
                             are_the_illuminati_real_chip_berlet  7.43M  3.14G  2.11M
                                       what_is_fat_george_zaidan  7.34M  3.15G  2.09M
       what_is_mccarthyism_and_how_did_it_happen_ellen_schrecker  9.78M  3.16G  2.08M
               the_complex_geometry_of_islamic_design_eric_broug  17.1M  3.18G  2.08M
              the_most_successful_pirate_of_all_time_dian_murray  8.43M  3.18G  2.08M
     how_to_use_rhetoric_to_get_what_you_want_camille_a_langston  6.38M  3.19G  2.07M
                                   why_do_we_hiccup_john_cameron  10.1M  3.20G  2.07M
    the_journey_to_pluto_the_farthest_world_ever_explored_alan_s  8.63M  3.21G  2.07M
                               what_is_schizophrenia_anees_bahji  10.5M  3.22G  2.06M
                                   rhapsody_on_the_proof_of_pi_4  21.3M  3.24G  2.06M
    the_silk_road_connecting_the_ancient_world_through_trade_sha  9.08M  3.25G  2.06M
               how_does_your_brain_respond_to_pain_karen_d_davis  9.89M  3.26G  2.06M
                         what_orwellian_really_means_noah_tavlin  18.6M  3.28G  2.06M
                                 how_smart_are_orangutans_lu_gao  6.85M  3.28G  2.05M
                           are_ghost_ships_real_peter_b_campbell  11.7M  3.29G  2.05M
                   whats_the_big_deal_with_gluten_william_d_chey  7.71M  3.30G  2.04M
    the_mathematical_secrets_of_pascals_triangle_wajdi_mohamed_r  6.80M  3.31G  2.04M
                       why_is_yawning_contagious_claudia_aguirre  10.5M  3.32G  2.03M
     how_do_nuclear_power_plants_work_m_v_ramana_and_sajan_saini  11.5M  3.33G  2.02M
                ancient_romes_most_notorious_doctor_ramon_glazov  8.17M  3.34G  2.02M
                     did_the_amazons_really_exist_adrienne_mayor  14.0M  3.35G  2.01M
            hawking_s_black_hole_paradox_explained_fabio_pacucci  11.2M  3.36G  2.00M
                                      comma_story_terisa_folaron  7.47M  3.37G  2.00M
             why_do_airlines_sell_too_many_tickets_nina_klietsch  6.11M  3.38G  2.00M
    how_many_ways_are_there_to_prove_the_pythagorean_theorem_bet  7.39M  3.38G  2.00M
             how_squids_outsmart_their_predators_carly_anne_york  9.54M  3.39G  2.00M
    the_difference_between_classical_and_operant_conditioning_pe  6.51M  3.40G  2.00M
                             what_causes_body_odor_mel_rosenberg  6.32M  3.40G  1.99M
         the_science_behind_the_myth_homer_s_odyssey_matt_kaplan  6.50M  3.41G  1.99M
       the_rise_and_fall_of_the_assyrian_empire_marian_h_feldman  12.1M  3.42G  1.98M
                            the_paradox_of_value_akshita_agarwal  7.73M  3.43G  1.98M
                   why_is_biodiversity_so_important_kim_preshoff  10.6M  3.44G  1.98M
                 can_you_solve_the_time_travel_riddle_dan_finkel  8.14M  3.45G  1.97M
                    why_its_so_hard_to_cure_hiv_aids_janet_iwasa  7.72M  3.46G  1.97M
    the_legend_of_annapurna_hindu_goddess_of_nourishment_antara_  8.40M  3.46G  1.97M
         music_and_math_the_genius_of_beethoven_natalya_st_clair  10.2M  3.47G  1.96M
                        einstein_s_miracle_year_larry_lagerstrom  7.55M  3.48G  1.96M
                          the_bug_that_poops_candy_george_zaidan  14.1M  3.50G  1.95M
                    will_we_ever_be_able_to_teleport_sajan_saini  17.3M  3.51G  1.95M
                 if_superpowers_were_real_super_strength_joy_lin  12.9M  3.53G  1.94M
                               inside_your_computer_bettina_bair  6.95M  3.53G  1.94M
    the_myth_of_oisin_and_the_land_of_eternal_youth_iseult_gille  8.19M  3.54G  1.94M
                   how_do_vaccines_work_kelwalin_dhanasarnsombut  6.41M  3.55G  1.92M
          what_is_the_tragedy_of_the_commons_nicholas_amendolare  12.4M  3.56G  1.91M
                  the_brilliance_of_bioluminescence_leslie_kenna  6.52M  3.56G  1.91M
                          can_we_eat_to_starve_cancer_william_li  35.4M  3.60G  1.90M
                   how_does_laser_eye_surgery_work_dan_reinstein  12.1M  3.61G  1.87M
     how_the_normans_changed_the_history_of_europe_mark_robinson  13.3M  3.62G  1.87M
         check_your_intuition_the_birthday_problem_david_knuffke  13.3M  3.64G  1.87M
              can_you_solve_the_trolls_paradox_riddle_dan_finkel  10.2M  3.65G  1.87M
    are_you_a_body_with_a_mind_or_a_mind_with_a_body_maryam_alim  10.6M  3.66G  1.87M
                         if_superpowers_were_real_flight_joy_lin  20.6M  3.68G  1.87M
              can_you_solve_the_vampire_hunter_riddle_dan_finkel  5.88M  3.68G  1.86M
                          a_brief_history_of_dogs_david_ian_howe  9.68M  3.69G  1.86M
    why_dont_poisonous_animals_poison_themselves_rebecca_d_tarvi  9.25M  3.70G  1.85M
            why_do_we_harvest_horseshoe_crab_blood_elizabeth_cox  7.50M  3.71G  1.85M
                    da_vinci_s_vitruvian_man_of_math_james_earle  6.30M  3.72G  1.84M
    situational_irony_the_opposite_of_what_you_think_christopher  5.88M  3.72G  1.84M
             why_should_you_read_fahrenheit_451_iseult_gillespie  9.36M  3.73G  1.83M
                                          insults_by_shakespeare  12.9M  3.74G  1.83M
                         the_history_of_tattoos_addison_anderson  10.3M  3.75G  1.83M
                         the_life_cycle_of_a_t_shirt_angel_chang  12.3M  3.76G  1.82M
    can_you_solve_the_cuddly_duddly_fuddly_wuddly_riddle_dan_fin  6.06M  3.77G  1.82M
                    how_to_spot_a_misleading_graph_lea_gaslowitz  8.34M  3.78G  1.82M
                         how_do_hard_drives_work_kanawat_senanan  17.8M  3.80G  1.82M
    population_pyramids_powerful_predictors_of_the_future_kim_pr  10.9M  3.81G  1.81M
                       how_aspirin_was_discovered_krishna_sudhir  11.6M  3.82G  1.81M
                 a_different_way_to_visualize_rhythm_john_varney  9.61M  3.83G  1.80M
    the_moral_roots_of_liberals_and_conservatives_jonathan_haidt  35.6M  3.86G  1.80M
               a_brief_history_of_banned_numbers_alessandra_king  7.66M  3.87G  1.79M
          the_greek_myth_of_talos_the_first_robot_adrienne_mayor  8.36M  3.88G  1.79M
             the_genius_of_mendeleev_s_periodic_table_lou_serico  7.03M  3.89G  1.78M
                can_you_solve_the_giant_iron_riddle_alex_gendler  5.39M  3.89G  1.77M
             how_do_dogs_see_with_their_noses_alexandra_horowitz  10.1M  3.90G  1.76M
    the_otherworldly_creatures_in_the_ocean_s_deepest_depths_lid  7.37M  3.91G  1.76M
             why_should_you_read_james_joyce_s_ulysses_sam_slote  18.6M  3.93G  1.76M
        the_colossal_consequences_of_supervolcanoes_alex_gendler  12.1M  3.94G  1.73M
                                  why_the_solar_system_can_exist  3.58M  3.94G  1.73M
    getting_started_as_a_dj_mixing_mashups_and_digital_turntable  32.6M  3.97G  1.73M
            can_you_solve_the_rebel_supplies_riddle_alex_gendler  8.80M  3.98G  1.72M
          why_are_we_so_attached_to_our_things_christian_jarrett  8.22M  3.99G  1.72M
                               what_does_the_liver_do_emma_bryce  5.81M  3.99G  1.72M
             will_there_ever_be_a_mile_high_skyscraper_stefan_al  9.17M  4.00G  1.71M
           the_surprising_reasons_animals_play_dead_tierney_thys  7.38M  4.01G  1.71M
          how_memories_form_and_how_we_lose_them_catharine_young  7.48M  4.02G  1.71M
                               who_is_sherlock_holmes_neil_mccaw  8.34M  4.03G  1.69M
    an_athlete_uses_physics_to_shatter_world_records_asaf_bar_yo  5.59M  4.03G  1.69M
              the_science_of_static_electricity_anuradha_bhagwat  6.29M  4.04G  1.69M
    how_does_the_nobel_peace_prize_work_adeline_cuvelier_and_tor  11.7M  4.05G  1.69M
            can_you_solve_the_killer_robo_ants_riddle_dan_finkel  9.24M  4.06G  1.69M
     why_is_herodotus_called_the_father_of_history_mark_robinson  7.87M  4.07G  1.68M
                                how_batteries_work_adam_jacobson  6.38M  4.07G  1.68M
    one_of_the_most_difficult_words_to_translate_krystian_aparta  6.00M  4.08G  1.68M
          why_should_you_read_dune_by_frank_herbert_dan_kwartler  12.1M  4.09G  1.67M
             what_does_this_symbol_actually_mean_adrian_treharne  8.34M  4.10G  1.67M
                                    how_do_lungs_work_emma_bryce  5.98M  4.10G  1.66M
                                     the_secret_life_of_plankton  18.3M  4.12G  1.66M
     vermicomposting_how_worms_can_reduce_our_waste_matthew_ross  6.59M  4.13G  1.65M
              can_you_solve_the_secret_sauce_riddle_alex_gendler  7.29M  4.14G  1.65M
    how_do_glasses_help_us_see_andrew_bastawrous_and_clare_gilbe  11.8M  4.15G  1.65M
      history_through_the_eyes_of_the_potato_leo_bear_mcguinness  7.60M  4.15G  1.64M
                          how_does_impeachment_work_alex_gendler  11.3M  4.17G  1.64M
     how_big_is_a_mole_not_the_animal_the_other_one_daniel_dulek  8.84M  4.17G  1.64M
      nature_s_smallest_factory_the_calvin_cycle_cathy_symington  9.70M  4.18G  1.64M
                    if_superpowers_were_real_super_speed_joy_lin  17.0M  4.20G  1.64M
            what_we_know_and_don_t_know_about_ebola_alex_gendler  8.20M  4.21G  1.64M
         you_are_your_microbes_jessica_green_and_karen_guillemin  8.29M  4.22G  1.63M
         the_greatest_machine_that_never_was_john_graham_cumming  21.4M  4.24G  1.63M
               the_chinese_myth_of_the_meddling_monk_shunan_teng  8.00M  4.25G  1.63M
    what_can_schrodinger_s_cat_teach_us_about_quantum_mechanics_  16.4M  4.26G  1.63M
    the_ferocious_predatory_dinosaurs_of_cretaceous_sahara_nizar  8.82M  4.27G  1.62M
    the_akune_brothers_siblings_on_opposite_sides_of_war_wendell  12.8M  4.28G  1.62M
                urbanization_and_the_future_of_cities_vance_kite  8.36M  4.29G  1.62M
                    what_happens_during_a_stroke_vaibhav_goswami  10.5M  4.30G  1.61M
                    is_math_discovered_or_invented_jeff_dekofsky  14.1M  4.31G  1.61M
             how_to_make_your_writing_funnier_cheri_steinkellner  8.83M  4.32G  1.60M
                     how_many_universes_are_there_chris_anderson  15.2M  4.34G  1.60M
          the_origin_of_countless_conspiracy_theories_patrickjmt  10.7M  4.35G  1.60M
                          inside_the_ant_colony_deborah_m_gordon  12.4M  4.36G  1.59M
                                  the_survival_of_the_sea_turtle  7.90M  4.37G  1.59M
    what_really_happened_to_the_library_of_alexandria_elizabeth_  8.42M  4.38G  1.58M
                         do_animals_have_language_michele_bishop  7.90M  4.38G  1.58M
       is_there_any_truth_to_the_king_arthur_legends_alan_lupack  15.0M  4.40G  1.58M
            the_mysterious_life_and_death_of_rasputin_eden_girma  8.68M  4.41G  1.58M
                         what_makes_a_poem_a_poem_melissa_kovacs  15.5M  4.42G  1.58M
    licking_bees_and_pulping_trees_the_reign_of_a_wasp_queen_ken  10.9M  4.43G  1.58M
    how_in_vitro_fertilization_ivf_works_nassim_assefi_and_brian  14.5M  4.45G  1.57M
           why_should_you_read_crime_and_punishment_alex_gendler  8.22M  4.46G  1.57M
                  how_fast_are_you_moving_right_now_tucker_hiatt  16.2M  4.47G  1.57M
                    could_we_actually_live_on_mars_mari_foroutan  8.45M  4.48G  1.56M
    how_to_speed_up_chemical_reactions_and_get_a_date_aaron_sams  11.1M  4.49G  1.56M
             how_to_make_your_writing_suspenseful_victoria_smith  8.44M  4.50G  1.55M
                                   the_truth_about_bats_amy_wray  15.6M  4.51G  1.55M
                            does_grammar_matter_andreea_s_calude  7.88M  4.52G  1.54M
    earworms_those_songs_that_get_stuck_in_your_head_elizabeth_h  8.60M  4.53G  1.54M
                        a_3d_atlas_of_the_universe_carter_emmart  18.8M  4.55G  1.53M
                               what_s_an_algorithm_david_j_malan  7.77M  4.56G  1.52M
              where_do_math_symbols_come_from_john_david_walters  10.6M  4.57G  1.52M
                 can_you_solve_the_alien_probe_riddle_dan_finkel  8.42M  4.57G  1.52M
    oxygens_surprisingly_complex_journey_through_your_body_enda_  10.3M  4.58G  1.52M
           what_happens_when_your_dna_is_damaged_monica_menesini  7.65M  4.59G  1.51M
             what_are_the_universal_human_rights_benedetta_berti  12.0M  4.60G  1.51M
           can_you_solve_the_dragon_jousting_riddle_alex_gendler  9.13M  4.61G  1.51M
                 is_fire_a_solid_a_liquid_or_a_gas_elizabeth_cox  9.93M  4.62G  1.50M
        it_s_a_church_it_s_a_mosque_it_s_hagia_sophia_kelly_wall  14.3M  4.64G  1.50M
        how_does_cancer_spread_through_the_body_ivan_seah_yu_jun  9.36M  4.64G  1.49M
                       what_is_metallic_glass_ashwini_bharathula  6.04M  4.65G  1.49M
    can_100_renewable_energy_power_the_world_federico_rosei_and_  9.36M  4.66G  1.49M
    the_basics_of_the_higgs_boson_dave_barney_and_steve_goldfarb  8.81M  4.67G  1.48M
                            is_radiation_dangerous_matt_anticole  9.42M  4.68G  1.48M
               how_rollercoasters_affect_your_body_brian_d_avery  9.21M  4.69G  1.47M
                           what_causes_constipation_heba_shaheed  5.30M  4.69G  1.46M
                  grammar_s_great_divide_the_oxford_comma_ted_ed  6.93M  4.70G  1.46M
    how_one_scientist_averted_a_national_health_crisis_andrea_to  13.0M  4.71G  1.45M
          why_should_you_read_the_handmaid_s_tale_naomi_r_mercer  11.2M  4.72G  1.45M
                            how_does_fracking_work_mia_nacamulli  8.50M  4.73G  1.45M
             why_should_you_read_virginia_woolf_iseult_gillespie  15.7M  4.75G  1.45M
    how_do_cancer_cells_behave_differently_from_healthy_ones_geo  11.7M  4.76G  1.44M
                       the_science_of_milk_jonathan_j_o_sullivan  9.02M  4.77G  1.43M
               how_does_your_body_know_you_re_full_hilary_coller  8.23M  4.77G  1.42M
        the_psychology_behind_irrational_decisions_sara_garofalo  6.80M  4.78G  1.42M
                         what_is_verbal_irony_christopher_warner  8.04M  4.79G  1.41M
                           your_body_vs_implants_kaitlyn_sadtler  11.4M  4.80G  1.41M
    how_the_world_s_longest_underwater_tunnel_was_built_alex_gen  9.61M  4.81G  1.40M
       a_day_in_the_life_of_a_mongolian_queen_anne_f_broadbridge  7.17M  4.82G  1.39M
                   why_do_we_have_to_wear_sunscreen_kevin_p_boyd  8.69M  4.82G  1.39M
                         what_happened_to_antimatter_rolf_landua  14.4M  4.84G  1.39M
            what_happens_when_continents_collide_juan_d_carrillo  13.3M  4.85G  1.39M
            what_happens_when_you_get_heat_stroke_douglas_j_casa  6.07M  4.86G  1.38M
               the_strange_case_of_the_cyclops_sheep_tien_nguyen  6.87M  4.86G  1.37M
                 can_you_solve_the_sea_monster_riddle_dan_finkel  12.4M  4.88G  1.37M
               the_surprising_cause_of_stomach_ulcers_rusha_modi  11.6M  4.89G  1.37M
    the_last_banana_a_thought_experiment_in_probability_leonardo  8.23M  4.90G  1.37M
    group_theory_101_how_to_play_a_rubiks_cube_like_a_piano_mich  7.58M  4.90G  1.36M
                                                        caffeine  12.8M  4.92G  1.36M
    how_many_ways_can_you_arrange_a_deck_of_cards_yannay_khaikin  5.19M  4.92G  1.35M
        is_there_a_disease_that_makes_us_love_cats_jaap_de_roode  9.03M  4.93G  1.35M
                           why_do_our_bodies_age_monica_menesini  8.17M  4.94G  1.35M
                   making_sense_of_irrational_numbers_ganesh_pai  5.69M  4.94G  1.35M
                                             one_is_one_or_is_it  5.82M  4.95G  1.35M
    how_can_you_change_someone_s_mind_hint_facts_aren_t_always_e  10.5M  4.96G  1.34M
             the_ancient_origins_of_the_olympics_armand_d_angour  9.25M  4.97G  1.34M
                   why_is_meningitis_so_dangerous_melvin_sanicas  9.77M  4.98G  1.34M
                               how_to_use_a_semicolon_emma_bryce  5.84M  4.98G  1.34M
                         ugly_history_witch_hunts_brian_a_pavlac  13.9M  5.00G  1.33M
                         why_do_we_feel_nostalgia_clay_routledge  7.37M  5.00G  1.32M
                                    how_do_we_smell_rose_eveleth  8.22M  5.01G  1.32M
          why_do_people_get_so_anxious_about_math_orly_rubinsten  6.01M  5.02G  1.32M
    titan_of_terror_the_dark_imagination_of_h_p_lovecraft_silvia  8.52M  5.03G  1.31M
              can_you_outsmart_this_logical_fallacy_alex_gendler  6.02M  5.03G  1.31M
    the_egyptian_myth_of_isis_and_the_seven_scorpions_alex_gendl  8.66M  5.04G  1.31M
    what_color_is_tuesday_exploring_synesthesia_richard_e_cytowi  9.95M  5.05G  1.30M
                    the_philosophy_of_cynicism_william_d_desmond  10.2M  5.06G  1.30M
    what_machiavellian_really_means_pazit_cahlon_and_alex_gendle  7.85M  5.07G  1.29M
                   why_isnt_the_netherlands_underwater_stefan_al  10.3M  5.08G  1.29M
                  the_2400_year_search_for_the_atom_theresa_doud  8.42M  5.09G  1.29M
    how_much_of_human_history_is_on_the_bottom_of_the_ocean_pete  9.33M  5.10G  1.29M
                   if_superpowers_were_real_invisibility_joy_lin  13.4M  5.11G  1.28M
                        how_x_rays_see_through_your_skin_ge_wang  8.37M  5.12G  1.28M
    what_you_might_not_know_about_the_declaration_of_independenc  7.85M  5.12G  1.28M
                   where_did_earths_water_come_from_zachary_metz  6.17M  5.13G  1.28M
       the_aztec_myth_of_the_unlikeliest_sun_god_kay_almere_read  12.1M  5.14G  1.28M
                       how_your_muscular_system_works_emma_bryce  8.63M  5.15G  1.27M
        what_happens_when_you_have_a_concussion_clifford_robbins  10.3M  5.16G  1.27M
                why_do_buildings_fall_in_earthquakes_vicki_v_may  11.3M  5.17G  1.27M
    the_history_of_the_barometer_and_how_it_works_asaf_bar_yosef  6.07M  5.18G  1.27M
            the_myth_of_loki_and_the_master_builder_alex_gendler  7.81M  5.19G  1.26M
          how_do_viruses_jump_from_animals_to_humans_ben_longdon  10.4M  5.20G  1.26M
                history_vs_augustus_peta_greenfield_alex_gendler  8.30M  5.20G  1.25M
                      if_superpowers_were_real_body_mass_joy_lin  21.6M  5.22G  1.25M
    why_should_you_read_lord_of_the_flies_by_william_golding_jil  12.0M  5.24G  1.25M
         a_3_minute_guide_to_the_bill_of_rights_belinda_stutzman  7.50M  5.24G  1.25M
            history_vs_henry_viii_mark_robinson_and_alex_gendler  7.82M  5.25G  1.25M
                                       what_is_love_brad_troeger  14.7M  5.27G  1.25M
    why_certain_naturally_occurring_wildfires_are_necessary_jim_  8.56M  5.27G  1.24M
            the_ethical_dilemma_of_self_driving_cars_patrick_lin  14.7M  5.29G  1.24M
                    the_threat_of_invasive_species_jennifer_klos  8.62M  5.30G  1.23M
                     the_mystery_of_motion_sickness_rose_eveleth  5.10M  5.30G  1.23M
         the_irish_myth_of_the_giant_s_causeway_iseult_gillespie  7.27M  5.31G  1.23M
                       how_do_geckos_defy_gravity_eleanor_nelsen  7.93M  5.32G  1.23M
    why_does_your_voice_change_as_you_get_older_shaylin_a_schund  11.9M  5.33G  1.22M
                          why_are_sharks_so_awesome_tierney_thys  12.3M  5.34G  1.22M
    when_will_the_next_mass_extinction_occur_borths_d_emic_and_p  12.7M  5.35G  1.21M
                                   ted_ed_youtube_channel_teaser  4.46M  5.36G  1.20M
                did_ancient_troy_really_exist_einav_zamir_dembin  9.00M  5.37G  1.20M
               working_backward_to_solve_problems_maurice_ashley  13.9M  5.38G  1.20M
                                    eye_vs_camera_michael_mauser  13.3M  5.39G  1.19M
                     can_a_black_hole_be_destroyed_fabio_pacucci  16.3M  5.41G  1.19M
                     the_law_of_conservation_of_mass_todd_ramsey  8.86M  5.42G  1.19M
                 what_is_the_universe_expanding_into_sajan_saini  12.3M  5.43G  1.18M
    why_does_ice_float_in_water_george_zaidan_and_charles_morton  8.04M  5.44G  1.18M
    how_playing_sports_benefits_your_body_and_your_brain_leah_la  8.94M  5.45G  1.18M
                             an_anti_hero_of_one_s_own_tim_adams  9.86M  5.45G  1.18M
                              who_won_the_space_race_jeff_steers  9.93M  5.46G  1.17M
                    how_does_chemotherapy_work_hyunsoo_joshua_no  12.9M  5.48G  1.17M
    the_math_behind_michael_jordans_legendary_hang_time_andy_pet  6.10M  5.48G  1.17M
                   inside_the_minds_of_animals_bryan_b_rasmussen  9.40M  5.49G  1.17M
                           how_false_news_can_spread_noah_tavlin  6.63M  5.50G  1.16M
    how_interpreters_juggle_two_languages_at_once_ewandro_magalh  15.2M  5.51G  1.16M
                     why_is_cotton_in_everything_michael_r_stiff  10.4M  5.52G  1.15M
    whats_the_difference_between_a_scientific_law_and_theory_mat  9.55M  5.53G  1.15M
                       the_dangers_of_mixing_drugs_celine_valery  14.3M  5.55G  1.15M
                 a_brief_history_of_melancholy_courtney_stephens  8.22M  5.56G  1.14M
    can_you_survive_nuclear_fallout_brooke_buddemeier_and_jessic  8.90M  5.56G  1.14M
                                  how_to_set_the_table_anna_post  4.52M  5.57G  1.14M
    the_myth_of_the_sampo_an_infinite_source_of_fortune_and_gree  11.9M  5.58G  1.14M
     can_you_solve_the_worlds_most_evil_wizard_riddle_dan_finkel  8.54M  5.59G  1.14M
    everything_changed_when_the_fire_crystal_got_stolen_alex_gen  9.03M  5.60G  1.14M
    the_fundamentals_of_space_time_part_1_andrew_pontzen_and_tom  7.99M  5.60G  1.13M
                             what_is_a_coronavirus_elizabeth_cox  8.85M  5.61G  1.13M
                          the_death_of_the_universe_renee_hlozek  6.52M  5.62G  1.12M
                the_secrets_of_mozarts_magic_flute_joshua_borths  7.25M  5.63G  1.12M
                    why_do_humans_have_a_third_eyelid_dorsa_amir  8.01M  5.63G  1.12M
         in_on_a_secret_that_s_dramatic_irony_christopher_warner  4.57M  5.64G  1.12M
            the_myth_of_jason_and_the_argonauts_iseult_gillespie  13.5M  5.65G  1.12M
                the_dark_history_of_iq_tests_stefan_c_dombrowski  12.8M  5.66G  1.12M
    everything_you_need_to_know_to_read_homer_s_odyssey_jill_das  10.2M  5.67G  1.11M
                               music_as_a_language_victor_wooten  15.5M  5.69G  1.11M
                             how_do_your_kidneys_work_emma_bryce  6.69M  5.70G  1.10M
    how_miscommunication_happens_and_how_to_avoid_it_katherine_h  8.33M  5.70G  1.10M
    how_the_konigsberg_bridge_problem_changed_mathematics_dan_va  7.79M  5.71G  1.10M
    why_shakespeare_loved_iambic_pentameter_david_t_freeman_and_  10.3M  5.72G  1.10M
       what_is_the_coldest_thing_in_the_world_lina_marieth_hoyos  5.77M  5.73G  1.10M
                    three_ways_the_universe_could_end_venus_keus  7.53M  5.74G  1.09M
             when_will_the_next_ice_age_happen_lorraine_lisiecki  8.03M  5.74G  1.09M
                the_princess_who_rewrote_history_leonora_neville  7.54M  5.75G  1.09M
       inside_okcupid_the_math_of_online_dating_christian_rudder  16.5M  5.77G  1.09M
    ted_ed_is_on_patreon_we_need_your_help_to_revolutionize_educ  5.87M  5.77G  1.08M
                           why_can_t_some_birds_fly_gillian_gibb  6.71M  5.78G  1.08M
      the_history_of_the_world_according_to_corn_chris_a_kniesly  14.0M  5.79G  1.08M
               the_wild_world_of_carnivorous_plants_kenny_coogan  7.90M  5.80G  1.07M
      calculating_the_odds_of_intelligent_alien_life_jill_tarter  20.3M  5.82G  1.07M
    the_science_of_stage_fright_and_how_to_overcome_it_mikael_ch  11.4M  5.83G  1.07M
                    the_evolution_of_the_human_eye_joshua_harvey  7.25M  5.84G  1.07M
                            on_reading_the_koran_lesley_hazleton  13.7M  5.85G  1.07M
                                what_are_stem_cells_craig_a_kohn  6.30M  5.86G  1.06M
                               how_do_crystals_work_graham_baird  12.4M  5.87G  1.06M
               why_should_you_read_edgar_allan_poe_scott_peeples  12.5M  5.88G  1.06M
                         could_we_create_dark_matter_rolf_landua  11.2M  5.89G  1.06M
            why_should_you_read_charles_dickens_iseult_gillespie  16.6M  5.91G  1.06M
                     is_light_a_particle_or_a_wave_colm_kelleher  10.4M  5.92G  1.06M
                          the_infinite_life_of_pi_reynaldo_lopes  6.66M  5.93G  1.06M
                    deep_ocean_mysteries_and_wonders_david_gallo  22.5M  5.95G  1.05M
       how_taking_a_bath_led_to_archimedes_principle_mark_salata  8.23M  5.96G  1.05M
        einstein_s_brilliant_mistake_entangled_states_chad_orzel  8.45M  5.96G  1.05M
                  the_wicked_wit_of_jane_austen_iseult_gillespie  15.8M  5.98G  1.04M
                         the_art_of_the_metaphor_jane_hirshfield  9.29M  5.99G  1.04M
                          why_is_being_scared_so_fun_margee_kerr  10.8M  6.00G  1.03M
                                    what_is_a_vector_david_huynh  5.96M  6.01G  1.03M
    does_the_wonderful_wizard_of_oz_have_a_hidden_message_david_  8.28M  6.01G  1.03M
                       when_is_water_safe_to_drink_mia_nacamulli  11.6M  6.02G  1.03M
        the_simple_story_of_photosynthesis_and_food_amanda_ooten  8.50M  6.03G  1.03M
                        the_prison_break_think_like_a_coder_ep_1  14.0M  6.05G  1.02M
    the_past_present_and_future_of_the_bubonic_plague_sharon_n_d  6.58M  6.05G  1.02M
                        try_something_new_for_30_days_matt_cutts  5.88M  6.06G  1.02M
                     why_are_human_bodies_asymmetrical_leo_q_wan  8.05M  6.07G  1.02M
                            how_did_english_evolve_kate_gardoqui  15.5M  6.08G  1.02M
     a_day_in_the_life_of_an_ancient_celtic_druid_philip_freeman  15.0M  6.10G  1.02M
                    the_mysterious_science_of_pain_joshua_w_pate  10.8M  6.11G  1.01M
          how_optical_illusions_trick_your_brain_nathan_s_jacobs  13.3M  6.12G  1.01M
                         five_fingers_of_evolution_paul_andersen  10.5M  6.13G  1.01M
                    what_is_alzheimer_s_disease_ivan_seah_yu_jun  8.69M  6.14G  1.01M
                the_city_of_walls_constantinople_lars_brownworth  6.94M  6.15G  1.01M
                 inside_the_killer_whale_matriarchy_darren_croft  13.1M  6.16G  1.00M
            the_upside_of_isolated_civilizations_jason_shipinski  8.37M  6.17G  1.00M
    the_turing_test_can_a_computer_pass_for_a_human_alex_gendler  11.1M  6.18G  0.99M
    what_makes_tuberculosis_tb_the_world_s_most_infectious_kille  7.24M  6.18G  0.99M
    the_murder_of_ancient_alexandria_s_greatest_scholar_soraya_f  13.5M  6.20G  0.99M
                       does_stress_cause_pimples_claudia_aguirre  6.20M  6.20G  0.99M
                             how_do_contraceptives_work_nwhunter  6.60M  6.21G  0.99M
        how_magellan_circumnavigated_the_globe_ewandro_magalhaes  15.8M  6.23G  0.98M
    how_did_polynesian_wayfinders_navigate_the_pacific_ocean_ala  18.1M  6.24G  0.98M
                      how_do_animals_see_in_the_dark_anna_stockl  12.7M  6.26G  0.98M
        the_breathtaking_courage_of_harriet_tubman_janell_hobson  8.17M  6.26G  0.98M
                                                         why_sex  12.5M  6.28G   997K
    everything_you_need_to_know_to_read_frankenstein_iseult_gill  9.18M  6.28G   993K
                    why_should_you_read_don_quixote_ilan_stavans  11.9M  6.30G   993K
                       surviving_a_nuclear_attack_irwin_redlener  44.7M  6.34G   990K
    how_the_world_s_first_metro_system_was_built_christian_wolma  8.97M  6.35G   987K
                     what_is_epigenetics_carlos_guerrero_bosagna  11.0M  6.36G   985K
                        why_don_t_oil_and_water_mix_john_pollard  14.7M  6.37G   981K
                   what_creates_a_total_solar_eclipse_andy_cohen  5.99M  6.38G   979K
    whats_so_great_about_the_great_lakes_cheri_dobbs_and_jennife  10.8M  6.39G   975K
                               how_menstruation_works_emma_bryce  8.57M  6.40G   973K
     the_beneficial_bacteria_that_make_delicious_food_erez_garty  7.20M  6.41G   973K
                can_you_solve_the_death_race_riddle_alex_gendler  13.6M  6.42G   969K
               the_art_forger_who_tricked_the_nazis_noah_charney  10.4M  6.43G   967K
               the_complicated_history_of_surfing_scott_laderman  14.1M  6.44G   966K
    turbulence_one_of_the_great_unsolved_mysteries_of_physics_to  13.1M  6.46G   961K
     what_if_cracks_in_concrete_could_fix_themselves_congrui_jin  8.21M  6.46G   957K
               the_beauty_of_data_visualization_david_mccandless  31.2M  6.49G   956K
    can_you_solve_the_multiverse_rescue_mission_riddle_dan_finke  13.3M  6.51G   955K
          beware_of_nominalizations_aka_zombie_nouns_helen_sword  11.3M  6.52G   951K
                           why_do_whales_sing_stephanie_sardelis  9.43M  6.53G   947K
         the_beginning_of_the_universe_for_beginners_tom_whyntie  5.87M  6.53G   944K
          how_the_monkey_king_escaped_the_underworld_shunan_teng  15.4M  6.55G   943K
                       sugar_hiding_in_plain_sight_robert_lustig  9.30M  6.56G   943K
                          history_vs_sigmund_freud_todd_dufresne  8.79M  6.57G   943K
    why_is_this_painting_so_captivating_james_earle_and_christin  6.89M  6.57G   943K
           ugly_history_the_1937_haitian_massacre_edward_paulino  17.8M  6.59G   939K
       can_you_solve_the_mondrian_squares_riddle_gordon_hamilton  5.64M  6.60G   938K
                     how_do_ocean_currents_work_jennifer_verduin  10.2M  6.61G   937K
                    newton_s_3_laws_with_a_bicycle_joshua_manley  10.6M  6.62G   937K
                           questions_no_one_knows_the_answers_to  4.20M  6.62G   936K
    what_causes_opioid_addiction_and_why_is_it_so_tough_to_comba  19.1M  6.64G   934K
    game_theory_challenge_can_you_predict_human_behavior_lucas_h  5.95M  6.64G   933K
                   the_life_cycle_of_a_neutron_star_david_lunney  11.0M  6.65G   931K
    the_psychology_of_post_traumatic_stress_disorder_joelle_rabo  22.0M  6.68G   926K
                  biodiesel_the_afterlife_of_oil_natascia_radice  7.48M  6.68G   920K
               are_food_preservatives_bad_for_you_eleanor_nelsen  7.47M  6.69G   918K
                                  how_to_grow_a_bone_nina_tandon  7.72M  6.70G   918K
                            who_was_confucius_bryan_w_van_norden  10.6M  6.71G   915K
                                  the_science_of_skin_emma_bryce  7.01M  6.72G   913K
                      how_to_spot_a_counterfeit_bill_tien_nguyen  8.01M  6.72G   913K
                            how_do_your_hormones_work_emma_bryce  9.95M  6.73G   910K
                                 how_do_scars_form_sarthak_sinha  6.02M  6.74G   910K
                    how_do_executive_orders_work_christina_greer  8.88M  6.75G   908K
                             what_is_dust_made_of_michael_marder  10.1M  6.76G   908K
                   how_statistics_can_be_misleading_mark_liddell  10.0M  6.77G   907K
                      where_do_new_words_come_from_marcel_danesi  9.27M  6.78G   905K
     why_we_love_repetition_in_music_elizabeth_hellmuth_margulis  8.06M  6.78G   903K
                      a_reality_check_on_renewables_david_mackay  33.4M  6.82G   901K
             a_brief_history_of_video_games_part_i_safwat_saleem  6.97M  6.82G   898K
                    how_does_hibernation_work_sheena_lee_faherty  9.83M  6.83G   889K
                    how_to_sequence_the_human_genome_mark_j_kiel  12.7M  6.85G   885K
        frida_kahlo_the_woman_behind_the_legend_iseult_gillespie  11.5M  6.86G   883K
                                     why_do_we_sweat_john_murnan  10.3M  6.87G   880K
        the_secret_student_resistance_to_hitler_iseult_gillespie  9.19M  6.88G   876K
      how_small_are_we_in_the_scale_of_the_universe_alex_hofeldt  9.16M  6.88G   875K
                 why_should_you_read_kurt_vonnegut_mia_nacamulli  10.6M  6.90G   875K
                                  how_we_see_color_colm_kelleher  10.7M  6.91G   873K
                              the_road_not_taken_by_robert_frost  3.83M  6.91G   868K
      a_clever_way_to_estimate_enormous_numbers_michael_mitchell  10.1M  6.92G   865K
                      how_tall_can_a_tree_grow_valentin_hammoudi  8.21M  6.93G   858K
                                why_do_we_pass_gas_purna_kashyap  13.2M  6.94G   854K
                                what_causes_heartburn_rusha_modi  11.5M  6.95G   854K
    what_is_a_butt_tuba_and_why_is_it_in_medieval_art_michelle_b  6.83M  6.96G   853K
                                      how_heavy_is_air_dan_quinn  9.90M  6.97G   852K
            can_you_solve_the_dark_matter_fuel_riddle_dan_finkel  7.74M  6.98G   850K
                     how_do_drugs_affect_the_brain_sara_garofalo  9.52M  6.98G   849K
    will_the_ocean_ever_run_out_of_fish_ayana_elizabeth_johnson_  8.77M  6.99G   841K
            should_we_get_rid_of_standardized_testing_arlo_kempf  10.2M  7.00G   840K
          how_does_the_thyroid_manage_your_metabolism_emma_bryce  7.16M  7.01G   836K
    what_does_it_mean_to_be_a_refugee_benedetta_berti_and_evelie  8.78M  7.02G   831K
                   the_terrors_of_sleep_paralysis_ami_angelowicz  10.7M  7.03G   827K
    is_it_possible_to_create_a_perfect_vacuum_rolf_landua_and_an  18.3M  7.05G   827K
                                logarithms_explained_steve_kelly  5.67M  7.05G   825K
                    how_mucus_keeps_us_healthy_katharina_ribbeck  7.94M  7.06G   823K
      would_winning_the_lottery_make_you_happier_raj_raghunathan  7.85M  7.07G   822K
              why_are_there_so_many_types_of_apples_theresa_doud  6.49M  7.07G   821K
               the_story_behind_the_boston_tea_party_ben_labaree  10.0M  7.08G   818K
                          how_do_you_know_whom_to_trust_ram_neta  10.2M  7.09G   818K
                       how_art_can_help_you_analyze_amy_e_herman  7.45M  7.10G   815K
    aphasia_the_disorder_that_makes_you_lose_your_words_susan_wo  14.1M  7.12G   813K
    particles_and_waves_the_central_mystery_of_quantum_mechanics  7.11M  7.12G   813K
                                           the_cockroach_beatbox  15.2M  7.14G   809K
      could_the_earth_be_swallowed_by_a_black_hole_fabio_pacucci  16.1M  7.15G   804K
    the_origins_of_ballet_jennifer_tortorello_and_adrienne_westw  8.08M  7.16G   801K
                 eli_the_eel_a_mysterious_migration_james_prosek  6.61M  7.17G   798K
            solving_the_puzzle_of_the_periodic_table_eric_rosado  9.56M  7.18G   797K
                      why_do_we_kiss_under_mistletoe_carlos_reif  6.59M  7.18G   792K
                      what_is_consciousness_michael_s_a_graziano  7.85M  7.19G   792K
       how_does_your_body_know_what_time_it_is_marco_a_sotomayor  7.91M  7.20G   789K
                     why_are_blue_whales_so_enormous_asha_de_vos  11.7M  7.21G   787K
                           the_higgs_field_explained_don_lincoln  11.4M  7.22G   785K
                        how_to_fossilize_yourself_phoebe_a_cohen  8.15M  7.23G   784K
    did_shakespeare_write_his_plays_natalya_st_clair_and_aaron_w  6.64M  7.24G   784K
    diagnosing_a_zombie_brain_and_body_part_one_tim_verstynen_br  6.56M  7.24G   783K
                the_taino_myth_of_the_cursed_creator_bill_keegan  10.9M  7.25G   783K
    from_pacifist_to_spy_wwiis_surprising_secret_agent_shrabani_  9.21M  7.26G   779K
          got_seeds_just_add_bleach_acid_and_sandpaper_mary_koga  4.99M  7.27G   778K
                          secrets_of_the_x_chromosome_robin_ball  6.36M  7.27G   778K
                             how_to_choose_your_news_damon_brown  6.41M  7.28G   777K
                          real_life_sunken_cities_peter_campbell  10.0M  7.29G   774K
    the_mighty_mathematics_of_the_lever_andy_peterson_and_zack_p  7.27M  7.30G   772K
                           what_is_the_world_wide_web_twila_camp  6.02M  7.30G   771K
    who_s_at_risk_for_colon_cancer_amit_h_sachdev_and_frank_g_gr  7.69M  7.31G   771K
           a_guide_to_the_energy_of_the_earth_joshua_m_sneideman  9.00M  7.32G   768K
           climate_change_earth_s_giant_game_of_tetris_joss_fong  4.57M  7.32G   765K
                                   what_is_obesity_mia_nacamulli  8.40M  7.33G   764K
    the_fundamentals_of_space_time_part_2_andrew_pontzen_and_tom  8.17M  7.34G   763K
    the_infamous_and_ingenious_ho_chi_minh_trail_cameron_paterso  13.7M  7.35G   762K
     why_do_you_need_to_get_a_flu_shot_every_year_melvin_sanicas  8.94M  7.36G   761K
    what_happens_if_you_cut_down_all_of_a_city_s_trees_stefan_al  14.9M  7.37G   756K
                 a_brief_history_of_plural_word_s_john_mcwhorter  8.01M  7.38G   748K
         why_should_you_read_kafka_on_the_shore_iseult_gillespie  14.2M  7.40G   740K
                 your_body_language_shapes_who_you_are_amy_cuddy  54.3M  7.45G   739K
            rosalind_franklin_dna_s_unsung_hero_claudio_l_guerra  7.82M  7.46G   737K
                  kabuki_the_people_s_dramatic_art_amanda_mattes  7.30M  7.46G   732K
                            how_do_ventilators_work_alex_gendler  12.1M  7.48G   731K
      how_does_your_smartphone_know_your_location_wilton_l_virgo  9.32M  7.49G   730K
    how_the_sandwich_was_invented_moments_of_vision_5_jessica_or  3.90M  7.49G   729K
                     what_are_gravitational_waves_amber_l_stuver  7.34M  7.50G   727K
              how_do_we_know_what_color_dinosaurs_were_len_bloch  7.76M  7.50G   727K
    whats_the_smallest_thing_in_the_universe_jonathan_butterwort  10.2M  7.51G   721K
               why_should_you_read_sylvia_plath_iseult_gillespie  10.9M  7.52G   720K
    the_uncertain_location_of_electrons_george_zaidan_and_charle  5.84M  7.53G   720K
    the_imaginary_king_who_changed_the_real_world_matteo_salvado  12.1M  7.54G   715K
                               the_maya_myth_of_the_morning_star  8.79M  7.55G   713K
    how_exactly_does_binary_code_work_jose_americo_n_l_f_de_frei  8.37M  7.56G   712K
    why_should_you_read_dantes_divine_comedy_sheila_marie_orfano  12.2M  7.57G   712K
                           how_transistors_work_gokul_j_krishnan  6.48M  7.58G   711K
             the_left_brain_vs_right_brain_myth_elizabeth_waters  12.2M  7.59G   711K
    gerrymandering_how_drawing_jagged_lines_can_impact_an_electi  7.17M  7.60G   706K
      what_happened_when_we_all_stopped_narrated_by_jane_goodall  6.08M  7.60G   703K
                                   claws_vs_nails_matthew_borths  7.38M  7.61G   700K
                                     what_is_color_colm_kelleher  7.20M  7.62G   699K
                                the_science_of_smog_kim_preshoff  8.11M  7.62G   699K
    how_do_germs_spread_and_why_do_they_make_us_sick_yannay_khai  6.55M  7.63G   697K
                     why_should_you_read_hamlet_iseult_gillespie  10.8M  7.64G   695K
    what_did_democracy_really_mean_in_athens_melissa_schwartzber  19.0M  7.66G   694K
                  how_did_clouds_get_their_names_richard_hamblyn  9.26M  7.67G   691K
                  a_day_in_the_life_of_an_aztec_midwife_kay_read  7.59M  7.68G   690K
    what_s_hidden_among_the_tallest_trees_on_earth_wendell_oshir  11.6M  7.69G   685K
    buffalo_buffalo_buffalo_one_word_sentences_and_how_they_work  5.00M  7.69G   681K
    the_meaning_of_life_according_to_simone_de_beauvoir_iseult_g  12.3M  7.70G   678K
                           when_to_use_apostrophes_laura_mcclure  5.63M  7.71G   678K
            radioactivity_expect_the_unexpected_steve_weatherall  9.30M  7.72G   674K
               who_built_great_zimbabwe_and_why_breeanna_elliott  8.88M  7.73G   671K
                          the_moon_illusion_andrew_vanden_heuvel  8.19M  7.74G   667K
    the_strengths_and_weaknesses_of_acids_and_bases_george_zaida  6.84M  7.74G   667K
    vultures_the_acid_puking_plague_busting_heroes_of_the_ecosys  9.34M  7.75G   665K
                    are_we_living_in_a_simulation_zohreh_davoudi  5.98M  7.76G   665K
                                rethinking_thinking_trevor_maber  13.7M  7.77G   659K
                          reasons_for_the_seasons_rebecca_kaplan  8.67M  7.78G   659K
                      what_causes_economic_bubbles_prateek_singh  9.45M  7.79G   657K
                what_causes_an_economic_recession_richard_coffin  7.43M  7.80G   656K
    the_case_of_the_missing_fractals_alex_rosenthal_and_george_z  21.3M  7.82G   654K
      how_the_bra_was_invented_moments_of_vision_1_jessica_oreck  3.36M  7.82G   654K
                        why_it_pays_to_work_hard_richard_st_john  15.8M  7.83G   652K
           the_mathematics_of_sidewalk_illusions_fumiko_futamura  13.4M  7.85G   648K
    looks_aren_t_everything_believe_me_i_m_a_model_cameron_russe  19.4M  7.87G   643K
                    does_stress_affect_your_memory_elizabeth_cox  8.10M  7.87G   642K
              what_is_leukemia_danilo_allegra_and_dania_puggioni  7.89M  7.88G   642K
            a_brief_history_of_numerical_systems_alessandra_king  6.81M  7.89G   640K
    how_polarity_makes_water_behave_strangely_christina_kleinber  7.16M  7.90G   640K
                                 life_of_an_astronaut_jerry_carr  8.86M  7.90G   640K
       ugly_history_japanese_american_incarceration_camps_densho  9.86M  7.91G   639K
                            what_does_the_pancreas_do_emma_bryce  7.01M  7.92G   639K
               how_turtle_shells_evolved_twice_judy_cebra_thomas  9.08M  7.93G   636K
    what_aristotle_and_joshua_bell_can_teach_us_about_persuasion  9.96M  7.94G   634K
               why_should_you_read_virgil_s_aeneid_mark_robinson  17.1M  7.96G   634K
                            how_to_spot_a_fad_diet_mia_nacamulli  7.10M  7.96G   632K
                       are_shakespeare_s_plays_encoded_within_pi  12.2M  7.98G   629K
    this_one_weird_trick_will_help_you_spot_clickbait_jeff_leek_  8.37M  7.98G   626K
           what_is_the_biggest_single_celled_organism_murry_gans  6.89M  7.99G   624K
                  the_case_of_the_vanishing_honeybees_emma_bryce  11.5M  8.00G   623K
        how_many_verb_tenses_are_there_in_english_anna_ananichuk  9.51M  8.01G   622K
      the_fascinating_science_behind_phantom_limbs_joshua_w_pate  12.2M  8.02G   620K
              can_wildlife_adapt_to_climate_change_erin_eastwood  10.7M  8.03G   619K
                    what_happened_to_trial_by_jury_suja_a_thomas  7.02M  8.04G   616K
    the_hidden_network_that_makes_the_internet_possible_sajan_sa  12.9M  8.05G   616K
                 how_atoms_bond_george_zaidan_and_charles_morton  5.04M  8.06G   615K
                            where_do_genes_come_from_carl_zimmer  8.08M  8.07G   614K
               how_close_are_we_to_eradicating_hiv_philip_a_chan  11.3M  8.08G   612K
              sunlight_is_way_older_than_you_think_sten_odenwald  7.77M  8.08G   609K
    why_are_earthquakes_so_hard_to_predict_jean_baptiste_p_koehl  9.91M  8.09G   609K
        is_there_a_limit_to_technological_progress_clement_vidal  8.32M  8.10G   608K
               the_neuroscience_of_imagination_andrey_vyshedskiy  17.5M  8.12G   606K
                            why_is_there_a_b_in_doubt_gina_cooke  4.63M  8.12G   605K
                               the_pangaea_pop_up_michael_molina  6.78M  8.13G   605K
       why_is_the_us_constitution_so_hard_to_amend_peter_paccone  8.32M  8.14G   601K
            light_waves_visible_and_invisible_lucianne_walkowicz  12.0M  8.15G   599K
    the_chaotic_brilliance_of_artist_jean_michel_basquiat_jordan  11.5M  8.16G   599K
    from_the_top_of_the_food_chain_down_rewilding_our_world_geor  10.1M  8.17G   598K
                             how_did_feathers_evolve_carl_zimmer  6.93M  8.18G   598K
                   how_long_will_human_impacts_last_david_biello  8.98M  8.19G   597K
    if_matter_falls_down_does_antimatter_fall_up_chloe_malbrunot  7.29M  8.19G   597K
    how_exposing_anonymous_companies_could_cut_down_on_crime_glo  10.1M  8.20G   592K
    could_human_civilization_spread_across_the_whole_galaxy_roey  8.02M  8.21G   591K
                         is_graffiti_art_or_vandalism_kelly_wall  15.2M  8.23G   590K
    the_romans_flooded_the_colosseum_for_sea_battles_janelle_pet  7.65M  8.23G   589K
                  could_your_brain_repair_itself_ralitsa_petrova  6.33M  8.24G   586K
                       a_brief_history_of_religion_in_art_ted_ed  14.8M  8.25G   585K
                                 everyday_leadership_drew_dudley  12.9M  8.27G   585K
    how_one_journalist_risked_her_life_to_hold_murderers_account  8.26M  8.28G   584K
    why_is_nasa_sending_a_spacecraft_to_a_metal_world_linda_t_el  8.76M  8.28G   584K
                              how_did_teeth_evolve_peter_s_ungar  12.0M  8.30G   583K
                          what_happens_if_you_guess_leigh_nataro  7.57M  8.30G   582K
           how_much_does_a_video_weigh_michael_stevens_of_vsauce  15.4M  8.32G   581K
    the_incredible_collaboration_behind_the_international_space_  9.79M  8.33G   580K
    everything_you_need_to_know_to_read_the_canterbury_tales_ise  8.15M  8.34G   580K
               why_the_insect_brain_is_so_incredible_anna_stockl  12.0M  8.35G   576K
    how_the_band_aid_was_invented_moments_of_vision_3_jessica_or  3.05M  8.35G   575K
    what_is_chemical_equilibrium_george_zaidan_and_charles_morto  8.02M  8.36G   575K
    notes_of_a_native_son_the_world_according_to_james_baldwin_c  7.73M  8.37G   573K
          why_should_you_read_waiting_for_godot_iseult_gillespie  10.1M  8.38G   572K
                   why_are_manhole_covers_round_marc_chamberland  6.85M  8.38G   571K
           are_we_running_out_of_clean_water_balsher_singh_sidhu  16.5M  8.40G   571K
         how_do_we_separate_the_seemingly_inseparable_iddo_magen  6.67M  8.40G   568K
    why_is_aristophanes_called_the_father_of_comedy_mark_robinso  11.0M  8.42G   566K
                how_we_think_complex_cells_evolved_adam_jacobson  9.84M  8.42G   565K
    are_spotty_fruits_and_vegetables_safe_to_eat_elizabeth_braue  7.13M  8.43G   565K
    why_aren_t_we_only_using_solar_power_alexandros_george_chara  10.8M  8.44G   564K
               why_is_this_painting_so_shocking_iseult_gillespie  10.2M  8.45G   563K
    how_do_us_supreme_court_justices_get_appointed_peter_paccone  8.46M  8.46G   562K
    is_there_a_center_of_the_universe_marjee_chmiel_and_trevor_o  9.33M  8.47G   562K
                             overcoming_obstacles_steven_claunch  11.5M  8.48G   558K
                           the_science_of_symmetry_colm_kelleher  15.5M  8.50G   556K
    dead_stuff_the_secret_ingredient_in_our_food_chain_john_c_mo  8.00M  8.50G   555K
                             the_coin_flip_conundrum_po_shen_loh  7.01M  8.51G   554K
    the_secret_language_of_trees_camille_defrenne_and_suzanne_si  8.80M  8.52G   547K
    how_this_disease_changes_the_shape_of_your_cells_amber_m_yat  11.2M  8.53G   547K
             why_do_people_fear_the_wrong_things_gerd_gigerenzer  8.68M  8.54G   546K
                    pixar_the_math_behind_the_movies_tony_derose  15.8M  8.55G   544K
             how_to_biohack_your_cells_to_fight_cancer_greg_foot  24.5M  8.58G   539K
              why_the_shape_of_your_screen_matters_brian_gervase  5.26M  8.58G   539K
    should_we_be_looking_for_life_elsewhere_in_the_universe_aoma  8.84M  8.59G   537K
          how_do_schools_of_fish_swim_in_harmony_nathan_s_jacobs  13.9M  8.61G   535K
                   become_a_slam_poet_in_five_steps_gayle_danley  11.5M  8.62G   534K
    the_accident_that_changed_the_world_allison_ramsey_and_mary_  7.87M  8.62G   533K
                               how_bones_make_blood_melody_smith  7.43M  8.63G   532K
                                walking_on_eggs_sick_science_069  2.07M  8.63G   532K
                         how_do_we_study_the_stars_yuan_sen_ting  9.96M  8.64G   531K
                        the_evolution_of_the_book_julie_dreyfuss  12.1M  8.66G   530K
                            how_do_focus_groups_work_hector_lanz  9.05M  8.66G   530K
                     how_fiction_can_change_reality_jessica_wise  8.99M  8.67G   528K
                 how_north_america_got_its_shape_peter_j_haproff  8.40M  8.68G   524K
                the_pleasure_of_poetic_pattern_david_silverstein  8.93M  8.69G   523K
    the_fundamentals_of_space_time_part_3_andrew_pontzen_and_tom  5.63M  8.70G   521K
    a_day_in_the_life_of_an_ancient_peruvian_shaman_gabriel_prie  7.63M  8.70G   517K
                      pizza_physics_new_york_style_colm_kelleher  7.80M  8.71G   516K
    feedback_loops_how_nature_gets_its_rhythms_anje_margriet_neu  14.5M  8.72G   516K
                         the_science_of_hearing_douglas_l_oliver  8.76M  8.73G   514K
             you_are_more_transparent_than_you_think_sajan_saini  9.69M  8.74G   512K
           animation_basics_the_art_of_timing_and_spacing_ted_ed  12.2M  8.75G   509K
       what_in_the_world_is_topological_quantum_matter_fan_zhang  7.40M  8.76G   507K
      can_you_find_the_next_number_in_this_sequence_alex_gendler  6.83M  8.77G   506K
    how_to_squeeze_electricity_out_of_crystals_ashwini_bharathul  13.1M  8.78G   505K
                     solid_liquid_gas_and_plasma_michael_murillo  15.6M  8.80G   504K
    one_of_the_most_epic_engineering_feats_in_history_alex_gendl  17.9M  8.81G   501K
                     how_crispr_lets_you_edit_dna_andrea_m_henle  8.32M  8.82G   500K
                   what_s_so_special_about_viking_ships_jan_bill  13.0M  8.83G   499K
    corruption_wealth_and_beauty_the_history_of_the_venetian_gon  11.4M  8.85G   498K
    cell_membranes_are_way_more_complicated_than_you_think_nazzy  14.6M  8.86G   498K
    why_wasnt_the_bill_of_rights_originally_in_the_us_constituti  9.62M  8.87G   497K
    the_exceptional_life_of_benjamin_banneker_rose_margaret_eken  6.56M  8.88G   497K
    the_truth_about_electroconvulsive_therapy_ect_helen_m_farrel  8.03M  8.88G   492K
                              how_to_live_to_be_100_dan_buettner  32.8M  8.92G   491K
                  the_power_of_a_great_introduction_carolyn_mohr  10.4M  8.93G   490K
      the_mysterious_origins_of_life_on_earth_luka_seamus_wright  11.0M  8.94G   489K
       is_there_a_difference_between_art_and_craft_laura_morelli  12.2M  8.95G   489K
                 what_triggers_a_chemical_reaction_kareem_jarrah  6.09M  8.95G   489K
                 the_battle_of_the_greek_tragedies_melanie_sirof  13.7M  8.97G   488K
                         what_are_mini_brains_madeline_lancaster  6.85M  8.97G   488K
    how_can_we_solve_the_antibiotic_resistance_crisis_gerry_wrig  11.9M  8.99G   485K
           are_naked_mole_rats_the_strangest_mammals_thomas_park  9.09M  8.99G   484K
               music_and_creativity_in_ancient_greece_tim_hansen  9.58M  9.00G   483K
             the_making_of_the_american_constitution_judy_walton  7.78M  9.01G   479K
                            the_power_of_passion_richard_st_john  15.5M  9.03G   479K
                            the_power_of_simple_words_terin_izil  3.90M  9.03G   476K
    how_inventions_change_history_for_better_and_for_worse_kenne  12.5M  9.04G   476K
                                              big_data_tim_smith  12.9M  9.06G   474K
        the_most_lightning_struck_place_on_earth_graeme_anderson  7.34M  9.06G   474K
            how_to_master_your_sense_of_smell_alexandra_horowitz  9.71M  9.07G   473K
       the_chemical_reaction_that_feeds_the_world_daniel_d_dulek  10.7M  9.08G   471K
    the_fight_for_the_right_to_vote_in_the_united_states_nicki_b  6.60M  9.09G   469K
                          the_resistance_think_like_a_coder_ep_2  11.9M  9.10G   468K
                                             electric_vocabulary  12.9M  9.11G   467K
             a_day_in_the_life_of_a_cossack_warrior_alex_gendler  14.2M  9.13G   466K
      four_ways_to_understand_the_earth_s_age_joshua_m_sneideman  10.1M  9.14G   465K
             the_power_of_creative_constraints_brandon_rodriguez  7.08M  9.14G   463K
                      how_do_blood_transfusions_work_bill_schutt  14.4M  9.16G   461K
    why_should_you_read_the_god_of_small_things_by_arundhati_roy  11.6M  9.17G   460K
    why_should_you_read_a_midsummer_night_s_dream_iseult_gillesp  13.0M  9.18G   459K
    the_many_meanings_of_michelangelo_s_statue_of_david_james_ea  5.54M  9.19G   459K
                        introducing_ted_ed_lessons_worth_sharing  6.73M  9.19G   457K
                         whats_a_smartphone_made_of_kim_preshoff  10.9M  9.20G   457K
       why_should_you_read_the_master_and_margarita_alex_gendler  7.97M  9.21G   455K
    how_quantum_mechanics_explains_global_warming_lieven_scheire  17.5M  9.23G   455K
                          why_are_fish_fish_shaped_lauren_sallan  11.9M  9.24G   449K
                               think_like_a_coder_teaser_trailer  2.39M  9.24G   448K
                       how_do_birds_learn_to_sing_partha_p_mitra  11.3M  9.25G   448K
                  is_our_universe_the_only_universe_brian_greene  44.1M  9.30G   446K
                   what_is_the_universe_made_of_dennis_wildfogel  11.3M  9.31G   445K
                            how_brass_instruments_work_al_cannon  12.8M  9.32G   443K
         what_s_the_definition_of_comedy_banana_addison_anderson  7.20M  9.33G   439K
    explore_cave_paintings_in_this_360deg_animated_cave_iseult_g  4.55M  9.33G   438K
        the_popularity_plight_and_poop_of_penguins_dyan_denapoli  12.8M  9.35G   437K
    not_all_scientific_studies_are_created_equal_david_h_schwart  6.23M  9.35G   436K
    how_a_few_scientists_transformed_the_way_we_think_about_dise  9.78M  9.36G   431K
    the_fundamental_theorem_of_arithmetic_computer_science_khan_  8.53M  9.37G   429K
                         can_animals_be_deceptive_eldridge_adams  7.42M  9.38G   429K
          master_the_art_of_public_speaking_with_ted_masterclass  5.27M  9.38G   429K
    the_punishable_perils_of_plagiarism_melissa_huseman_d_annunz  8.44M  9.39G   428K
      how_braille_was_invented_moments_of_vision_9_jessica_oreck  2.98M  9.39G   428K
      how_far_would_you_have_to_go_to_escape_gravity_rene_laufer  10.8M  9.40G   425K
    how_blue_jeans_were_invented_moments_of_vision_10_jessica_or  3.82M  9.41G   422K
        how_coffee_got_quicker_moments_of_vision_2_jessica_oreck  4.18M  9.41G   421K
                                  dna_the_book_of_you_joe_hanson  13.5M  9.42G   418K
              what_s_below_the_tip_of_the_iceberg_camille_seaman  8.67M  9.43G   416K
    what_is_hpv_and_how_can_you_protect_yourself_from_it_emma_br  5.88M  9.44G   415K
         how_to_organize_add_and_multiply_matrices_bill_shillito  7.01M  9.45G   413K
    the_historical_audacity_of_the_louisiana_purchase_judy_walto  11.2M  9.46G   412K
                   how_do_virus_tests_actually_work_cella_wright  10.7M  9.47G   411K
                        why_tragedies_are_alluring_david_e_rivas  9.11M  9.48G   411K
                         the_importance_of_focus_richard_st_john  13.8M  9.49G   411K
    the_effects_of_underwater_pressure_on_the_body_neosha_s_kash  6.97M  9.50G   411K
    there_may_be_extraterrestrial_life_in_our_solar_system_augus  12.8M  9.51G   411K
                           how_to_create_cleaner_coal_emma_bryce  9.86M  9.52G   410K
                    the_sexual_deception_of_orchids_anne_gaskett  11.7M  9.53G   408K
    gyotaku_the_ancient_japanese_art_of_printing_fish_k_erica_do  9.13M  9.54G   406K
                   the_first_and_last_king_of_haiti_marlene_daut  8.84M  9.55G   404K
                                what_is_an_aurora_michael_molina  12.8M  9.56G   402K
                                             ted_ed_website_tour  7.12M  9.57G   401K
          how_misused_modifiers_can_hurt_your_writing_emma_bryce  5.25M  9.57G   400K
         the_contributions_of_female_explorers_courtney_stephens  9.09M  9.58G   399K
    why_should_you_read_shakespeares_the_tempest_iseult_gillespi  12.0M  9.59G   399K
    what_is_phantom_traffic_and_why_is_it_ruining_your_life_benj  10.0M  9.60G   397K
    how_the_popsicle_was_invented_moments_of_vision_11_jessica_o  3.61M  9.61G   396K
                       the_case_against_good_and_bad_marlee_neel  10.4M  9.62G   396K
                             can_robots_be_creative_gil_weinberg  8.49M  9.62G   393K
               the_race_to_sequence_the_human_genome_tien_nguyen  10.8M  9.63G   393K
               which_sunscreen_should_you_choose_mary_poffenroth  8.04M  9.64G   392K
    fresh_water_scarcity_an_introduction_to_the_problem_christia  4.98M  9.65G   392K
                    why_should_you_read_moby_dick_sascha_morrell  13.7M  9.66G   391K
                        who_decides_what_art_means_hayley_levitt  6.96M  9.67G   389K
                         would_you_live_on_the_moon_alex_gendler  9.05M  9.68G   387K
    a_needle_in_countless_haystacks_finding_habitable_worlds_ari  15.8M  9.69G   386K
                         the_science_of_snowflakes_marusa_bradac  7.73M  9.70G   386K
                              why_do_we_have_museums_j_v_maranto  11.7M  9.71G   386K
          the_coelacanth_a_living_fossil_of_a_fish_erin_eastwood  10.7M  9.72G   385K
    how_does_an_atom_smashing_particle_accelerator_work_don_linc  6.99M  9.73G   385K
                  the_lovable_and_lethal_sea_lion_claire_simeone  8.83M  9.74G   385K
          an_introduction_to_mathematical_theorems_scott_kennedy  9.47M  9.75G   384K
    how_the_bendy_straw_was_invented_moments_of_vision_12_jessic  3.05M  9.75G   384K
                               the_true_story_of_true_gina_cooke  16.2M  9.76G   380K
                          when_to_use_me_myself_and_i_emma_bryce  5.59M  9.77G   379K
                            the_world_s_english_mania_jay_walker  10.2M  9.78G   375K
         cicadas_the_dormant_army_beneath_your_feet_rose_eveleth  5.00M  9.78G   375K
                           gravity_and_the_human_body_jay_buckey  7.82M  9.79G   375K
                               why_do_americans_vote_on_tuesdays  7.96M  9.80G   375K
    why_havent_we_cured_arthritis_kaitlyn_sadtler_and_heather_j_  6.52M  9.81G   374K
                    how_containerization_shaped_the_modern_world  11.4M  9.82G   374K
                       why_neutrinos_matter_silvia_bravo_gallart  6.62M  9.82G   373K
    haptography_digitizing_our_sense_of_touch_katherine_kuchenbe  13.9M  9.84G   373K
    the_history_of_african_american_social_dance_camille_a_brown  17.2M  9.85G   373K
                tycho_brahe_the_scandalous_astronomer_dan_wenkel  11.4M  9.87G   370K
          will_future_spacecraft_fit_in_our_pockets_dhonam_pemba  8.31M  9.87G   369K
                              birth_of_a_nickname_john_mcwhorter  7.97M  9.88G   369K
     the_science_of_macaroni_salad_what_s_in_a_mixture_josh_kurz  7.48M  9.89G   368K
                                   where_did_the_earth_come_from  10.5M  9.90G   367K
    the_operating_system_of_life_george_zaidan_and_charles_morto  7.67M  9.91G   366K
    learning_from_smallpox_how_to_eradicate_a_disease_julie_garo  9.37M  9.92G   366K
                  what_is_abstract_expressionism_sarah_rosenthal  15.2M  9.93G   364K
            why_do_people_have_seasonal_allergies_eleanor_nelsen  15.2M  9.95G   364K
     how_computers_translate_human_language_ioannis_papachimonas  11.6M  9.96G   360K
                        the_furnace_bots_think_like_a_coder_ep_3  11.3M  9.97G   360K
                   shakespearean_dating_tips_anthony_john_peters  4.48M  9.97G   356K
                     how_algorithms_shape_our_world_kevin_slavin  37.2M  10.0G   356K
                             what_is_a_gift_economy_alex_gendler  7.23M  10.0G   356K
    how_super_glue_was_invented_moments_of_vision_8_jessica_orec  3.37M  10.0G   355K
                do_we_really_need_pesticides_fernan_perez_galvez  10.1M  10.0G   353K
                      attack_of_the_killer_algae_eric_noel_munoz  7.21M  10.0G   348K
    how_i_responded_to_sexism_in_gaming_with_empathy_lilian_chen  10.8M  10.0G   347K
    how_the_stethoscope_was_invented_moments_of_vision_7_jessica  3.79M  10.0G   347K
      whats_a_squillo_and_why_do_opera_singers_need_it_ming_luke  16.3M  10.1G   346K
            the_secret_messages_of_viking_runestones_jesse_byock  6.43M  10.1G   343K
    the_controversial_origins_of_the_encyclopedia_addison_anders  12.6M  10.1G   341K
                         the_train_heist_think_like_a_coder_ep_4  14.6M  10.1G   341K
    illuminating_photography_from_camera_obscura_to_camera_phone  7.92M  10.1G   341K
                                 how_to_grow_a_glacier_m_jackson  8.76M  10.1G   340K
        what_can_you_learn_from_ancient_skeletons_farnaz_khatibi  8.48M  10.1G   339K
              what_cameras_see_that_our_eyes_don_t_bill_shribman  6.84M  10.1G   336K
    how_the_rubber_glove_was_invented_moments_of_vision_4_jessic  3.30M  10.1G   335K
                could_we_survive_prolonged_space_travel_lisa_nip  12.7M  10.1G   335K
                                how_bacteria_talk_bonnie_bassler  40.1M  10.2G   334K
    how_to_speak_monkey_the_language_of_cotton_top_tamarins_anne  11.5M  10.2G   332K
                                 how_do_nerves_work_elliot_krane  11.9M  10.2G   332K
                  lets_plant_20_million_trees_together_teamtrees  2.39M  10.2G   332K
        this_sea_creature_breathes_through_its_butt_cella_wright  11.5M  10.2G   330K
                        the_chemistry_of_cold_packs_john_pollard  8.04M  10.2G   330K
             the_wildly_complex_anatomy_of_a_sneaker_angel_chang  9.13M  10.2G   329K
                    do_politics_make_us_irrational_jay_van_bavel  13.2M  10.3G   328K
    why_do_americans_and_canadians_celebrate_labor_day_kenneth_c  13.1M  10.3G   328K
    the_suns_surprising_movement_across_the_sky_gordon_williamso  7.46M  10.3G   327K
    can_you_spot_the_problem_with_these_headlines_level_1_jeff_l  9.34M  10.3G   326K
                 the_ballet_that_incited_a_riot_iseult_gillespie  11.4M  10.3G   326K
    how_close_are_we_to_uploading_our_minds_michael_s_a_graziano  8.59M  10.3G   324K
            who_was_the_world_s_first_author_soraya_field_fiorio  9.72M  10.3G   324K
        how_do_brain_scans_work_john_borghi_and_elizabeth_waters  9.10M  10.3G   323K
                    the_best_stats_you_ve_ever_seen_hans_rosling  36.0M  10.4G   322K
      is_there_a_reproducibility_crisis_in_science_matt_anticole  9.31M  10.4G   321K
    the_high_stakes_race_to_make_quantum_computers_work_chiara_d  9.41M  10.4G   320K
    how_to_visualize_one_part_per_million_kim_preshoff_the_ted_e  5.68M  10.4G   318K
           is_dna_the_future_of_data_storage_leo_bear_mcguinness  18.0M  10.4G   318K
                         learn_to_read_chinese_with_ease_shaolan  8.99M  10.4G   318K
    lessons_from_auschwitz_the_power_of_our_words_benjamin_zande  3.24M  10.4G   318K
                how_people_rationalize_fraud_kelly_richmond_pope  13.4M  10.4G   317K
                               how_life_begins_in_the_deep_ocean  18.1M  10.4G   316K
               where_we_get_our_fresh_water_christiana_z_peppard  6.66M  10.4G   314K
                         the_end_of_history_illusion_bence_nanay  5.94M  10.4G   314K
                          rapid_prototyping_google_glass_tom_chi  19.1M  10.5G   314K
                           the_twisting_tale_of_dna_judith_hauck  12.6M  10.5G   313K
                    can_plants_talk_to_each_other_richard_karban  14.5M  10.5G   312K
           how_does_math_guide_our_ships_at_sea_george_christoph  9.91M  10.5G   309K
                the_hidden_life_of_rosa_parks_riche_d_richardson  11.7M  10.5G   306K
              the_physics_of_playing_guitar_oscar_fernando_perez  15.3M  10.5G   306K
                        how_do_self_driving_cars_see_sajan_saini  9.03M  10.5G   303K
                 why_is_it_so_hard_to_cure_als_fernando_g_vieira  10.4M  10.5G   302K
                               disappearing_frogs_kerry_m_kriger  5.68M  10.6G   300K
         why_should_you_read_midnights_children_iseult_gillespie  19.5M  10.6G   300K
                how_to_build_a_dark_matter_detector_jenna_saffin  11.5M  10.6G   299K
    how_spontaneous_brain_activity_keeps_you_alive_nathan_s_jaco  9.08M  10.6G   298K
                       is_space_trying_to_kill_us_ron_shaneyfelt  6.67M  10.6G   295K
     what_did_dogs_teach_humans_about_diabetes_duncan_c_ferguson  6.39M  10.6G   295K
                               the_physics_of_surfing_nick_pizzo  11.1M  10.6G   293K
                             making_sense_of_spelling_gina_cooke  6.93M  10.6G   289K
                                              the_opposites_game  13.1M  10.6G   288K
                               the_chasm_think_like_a_coder_ep_6  16.3M  10.7G   287K
    a_poetic_experiment_walt_whitman_interpreted_by_three_animat  10.1M  10.7G   286K
                 poetic_stickup_put_the_financial_aid_in_the_bag  11.9M  10.7G   286K
                                        introducing_earth_school  2.24M  10.7G   285K
    the_microbial_jungles_all_over_the_place_and_you_scott_chimi  10.3M  10.7G   284K
                   the_tower_of_epiphany_think_like_a_coder_ep_7  19.5M  10.7G   284K
    how_smudge_proof_lipstick_was_invented_moments_of_vision_6_j  4.12M  10.7G   283K
           under_the_hood_the_chemistry_of_cars_cynthia_chubbuck  6.16M  10.7G   282K
                  all_the_world_s_a_stage_by_william_shakespeare  5.65M  10.7G   279K
               the_world_needs_all_kinds_of_minds_temple_grandin  48.2M  10.8G   276K
          the_history_of_our_world_in_18_minutes_david_christian  35.7M  10.8G   274K
                can_machines_read_your_emotions_kostas_karpouzis  7.50M  10.8G   273K
                    why_do_animals_form_swarms_maria_r_d_orsogna  18.5M  10.8G   272K
                         how_to_think_about_gravity_jon_bergmann  8.26M  10.8G   272K
                                       first_kiss_by_tim_seibles  5.95M  10.8G   270K
    romance_and_revolution_the_poetry_of_pablo_neruda_ilan_stava  15.3M  10.9G   269K
                             the_artists_think_like_a_coder_ep_5  14.2M  10.9G   269K
                            the_gauntlet_think_like_a_coder_ep_8  20.3M  10.9G   268K
                            the_time_value_of_money_german_nande  5.93M  10.9G   268K
            how_ancient_art_influenced_modern_art_felipe_galindo  13.9M  10.9G   268K
                       could_a_blind_eye_regenerate_david_davila  8.95M  10.9G   266K
            infinity_according_to_jorge_luis_borges_ilan_stavans  7.98M  10.9G   264K
           why_should_you_read_flannery_oconnor_iseult_gillespie  7.06M  10.9G   263K
          rnai_slicing_dicing_and_serving_your_cells_alex_dainis  7.38M  10.9G   262K
                the_first_asteroid_ever_discovered_carrie_nugent  7.50M  10.9G   262K
                the_cancer_gene_we_all_have_michael_windelspecht  6.82M  11.0G   261K
                              the_carbon_cycle_nathaniel_manning  9.35M  11.0G   260K
                           whats_the_point_e_of_ballet_ming_luke  13.0M  11.0G   258K
    all_of_the_energy_in_the_universe_is_george_zaidan_and_charl  10.7M  11.0G   258K
               the_poet_who_painted_with_his_words_genevieve_emy  8.16M  11.0G   258K
                                                dear_subscribers  8.46M  11.0G   255K
         are_there_universal_expressions_of_emotion_sophie_zadeh  8.79M  11.0G   254K
    forget_shopping_soon_you_ll_download_your_new_clothes_danit_  16.3M  11.0G   254K
    how_science_fiction_can_help_predict_the_future_roey_tzezana  17.6M  11.0G   254K
    from_aaliyah_to_jay_z_captured_moments_in_hip_hop_history_jo  12.2M  11.1G   254K
                     ideasthesia_how_do_ideas_feel_danko_nikolic  8.36M  11.1G   254K
    diagnosing_a_zombie_brain_and_behavior_part_two_tim_verstyne  6.01M  11.1G   253K
                would_you_weigh_less_in_an_elevator_carol_hedden  8.40M  11.1G   252K
                                how_breathing_works_nirvair_kaur  10.1M  11.1G   252K
                 et_is_probably_out_there_get_ready_seth_shostak  31.7M  11.1G   252K
    the_weird_and_wonderful_metamorphosis_of_the_butterfly_franz  10.4M  11.1G   251K
    symbiosis_a_surprising_tale_of_species_cooperation_david_gon  6.18M  11.1G   251K
                     hacking_bacteria_to_fight_cancer_tal_danino  11.5M  11.1G   250K
                               how_plants_tell_time_dasha_savage  7.16M  11.2G   250K
    underwater_farms_vs_climate_change_ayana_elizabeth_johnson_a  12.2M  11.2G   250K
    the_life_legacy_assassination_of_an_african_revolutionary_li  18.6M  11.2G   248K
          what_we_can_learn_from_galaxies_far_far_away_henry_lin  13.7M  11.2G   247K
                      who_controls_the_world_james_b_glattfelder  25.8M  11.2G   245K
    nasas_first_software_engineer_margaret_hamilton_matt_porter_  10.1M  11.2G   243K
                               let_s_talk_about_dying_peter_saul  22.7M  11.3G   242K
               how_to_turn_protest_into_powerful_change_eric_liu  10.0M  11.3G   242K
    the_historic_womens_suffrage_march_on_washington_michelle_me  10.7M  11.3G   241K
                     who_is_alexander_von_humboldt_george_mehler  9.36M  11.3G   238K
                the_invisible_motion_of_still_objects_ran_tivony  10.6M  11.3G   238K
         what_light_can_teach_us_about_the_universe_pete_edwards  10.5M  11.3G   236K
                     india_s_invisible_innovation_nirmalya_kumar  24.6M  11.3G   235K
                        why_i_m_a_weekday_vegetarian_graham_hill  8.79M  11.3G   233K
                       the_second_coming_by_william_butler_yeats  2.32M  11.3G   232K
    what_is_the_shape_of_a_molecule_george_zaidan_and_charles_mo  5.74M  11.3G   231K
         if_superpowers_were_real_which_would_you_choose_joy_lin  6.26M  11.4G   230K
                           the_great_brain_debate_ted_altschuler  13.4M  11.4G   227K
                  a_simple_way_to_tell_insects_apart_anika_hazra  6.46M  11.4G   226K
                                       accents_by_denice_frohman  9.39M  11.4G   224K
      how_one_scientist_took_on_the_chemical_industry_mark_lytle  12.0M  11.4G   224K
                               how_i_discovered_dna_james_watson  34.2M  11.4G   222K
             the_nurdles_quest_for_ocean_domination_kim_preshoff  9.76M  11.4G   221K
                       how_to_3d_print_human_tissue_taneka_jones  7.60M  11.4G   221K
    the_electrifying_speeches_of_sojourner_truth_daina_ramey_ber  9.68M  11.5G   220K
                           how_movies_teach_manhood_colin_stokes  23.3M  11.5G   219K
           the_dangerous_race_for_the_south_pole_elizabeth_leane  7.29M  11.5G   217K
    what_is_chirality_and_how_did_it_get_in_my_molecules_michael  8.29M  11.5G   217K
                                how_does_work_work_peter_bohacek  13.5M  11.5G   215K
                      the_key_to_media_s_hidden_codes_ben_beaton  19.2M  11.5G   214K
    why_do_hospitals_have_particle_accelerators_pedro_brugarolas  6.70M  11.5G   214K
    why_should_you_read_sci_fi_superstar_octavia_e_butler_ayana_  9.27M  11.5G   212K
    the_hidden_worlds_within_natural_history_museums_joshua_drew  7.12M  11.5G   212K
                     the_secret_lives_of_baby_fish_amy_mcdermott  10.4M  11.6G   211K
                           to_make_use_of_water_by_safia_elhillo  4.22M  11.6G   211K
    what_makes_neon_signs_glow_a_360deg_animation_michael_lipman  9.23M  11.6G   211K
                     the_game_changing_amniotic_egg_april_tucker  10.7M  11.6G   208K
                    making_a_ted_ed_lesson_visualizing_big_ideas  10.7M  11.6G   207K
    beach_bodies_in_spoken_word_david_fasanya_and_gabriel_barral  11.1M  11.6G   207K
    equality_sports_and_title_ix_erin_buzuvis_and_kristine_newha  9.10M  11.6G   204K
     the_dust_bunnies_that_built_our_planet_lorin_swint_matthews  12.9M  11.6G   203K
     an_unsung_hero_of_the_civil_rights_movement_christina_greer  9.65M  11.6G   201K
        want_to_be_an_activist_start_with_your_toys_mckenna_pope  15.9M  11.6G   197K
                                a_host_of_heroes_april_gudenrath  13.9M  11.7G   197K
              mining_literature_for_deeper_meanings_amy_e_harter  7.89M  11.7G   196K
    the_science_of_macaroni_salad_what_s_in_a_molecule_josh_kurz  7.34M  11.7G   194K
                               the_nutritionist_by_andrea_gibson  8.67M  11.7G   193K
    from_dna_to_silly_putty_the_diverse_world_of_polymers_jan_ma  13.1M  11.7G   192K
                                   the_tribes_we_lead_seth_godin  34.8M  11.7G   190K
         let_s_make_history_by_recording_it_storycorps_ted_prize  7.31M  11.7G   190K
      mysteries_of_vernacular_odd_jessica_oreck_and_rachael_teel  2.67M  11.7G   190K
     the_oddities_of_the_first_american_election_kenneth_c_davis  14.8M  11.8G   188K
                    write_your_story_change_history_brad_meltzer  14.9M  11.8G   186K
                                         beatboxing_101_beat_nyc  20.4M  11.8G   186K
               the_real_origin_of_the_franchise_sir_harold_evans  16.9M  11.8G   185K
                                how_to_fool_a_gps_todd_humphreys  29.0M  11.8G   183K
            making_sense_of_how_life_fits_together_bobbi_seleski  7.42M  11.8G   183K
       harvey_milk_s_radical_vision_of_equality_lillian_faderman  9.26M  11.8G   182K
                   how_social_media_can_make_history_clay_shirky  31.6M  11.9G   180K
    making_waves_the_power_of_concentration_gradients_sasha_wrig  9.82M  11.9G   178K
                        how_to_detect_a_supernova_samantha_kuula  10.5M  11.9G   178K
                    what_adults_can_learn_from_kids_adora_svitak  16.5M  11.9G   176K
    insights_into_cell_membranes_via_dish_detergent_ethan_perlst  6.72M  11.9G   176K
            what_if_we_could_look_inside_human_brains_moran_cerf  13.9M  11.9G   175K
        pros_and_cons_of_public_opinion_polls_jason_robert_jaffe  6.46M  11.9G   174K
                      free_falling_in_outer_space_matt_j_carlson  4.53M  11.9G   172K
                              the_power_of_introverts_susan_cain  35.7M  12.0G   172K
                                       network_theory_marc_samet  6.86M  12.0G   171K
      ode_to_the_only_black_kid_in_the_class_poem_by_clint_smith  1.76M  12.0G   169K
                       the_history_of_keeping_time_karen_mensing  9.31M  12.0G   169K
                            sunflowers_and_fibonacci_numberphile  17.5M  12.0G   169K
                             stroke_of_insight_jill_bolte_taylor  44.4M  12.1G   168K
    why_should_you_read_the_joy_luck_club_by_amy_tan_sheila_mari  6.08M  12.1G   168K
                                    new_colossus_by_emma_lazarus  1.98M  12.1G   168K
     a_curable_condition_that_causes_blindness_andrew_bastawrous  5.69M  12.1G   167K
    how_did_trains_standardize_time_in_the_united_states_william  7.29M  12.1G   167K
            networking_for_the_networking_averse_lisa_green_chau  7.31M  12.1G   166K
                                       start_a_ted_ed_club_today  4.62M  12.1G   160K
                bird_migration_a_perilous_journey_alyssa_klavans  7.10M  12.1G   159K
    is_our_climate_headed_for_a_mathematical_tipping_point_victo  8.10M  12.1G   158K
    activation_energy_kickstarting_chemical_reactions_vance_kite  8.80M  12.1G   157K
                       your_brain_on_video_games_daphne_bavelier  28.8M  12.1G   156K
    cloudy_climate_change_how_clouds_affect_earth_s_temperature_  19.7M  12.2G   154K
              could_a_breathalyzer_detect_cancer_julian_burschka  7.64M  12.2G   148K
                               what_on_earth_is_spin_brian_jones  12.1M  12.2G   148K
    why_the_arctic_is_climate_change_s_canary_in_the_coal_mine_w  7.75M  12.2G   147K
                     the_happy_secret_to_better_work_shawn_achor  23.2M  12.2G   147K
          animation_basics_the_optical_illusion_of_motion_ted_ed  14.6M  12.2G   147K
                            for_estefani_poem_by_aracelis_girmay  13.8M  12.2G   146K
                   slowing_down_time_in_writing_film_aaron_sitze  13.8M  12.3G   145K
                      mosquitos_malaria_and_education_bill_gates  61.1M  12.3G   145K
                                         evolution_in_a_big_city  11.5M  12.3G   144K
            the_magic_of_qr_codes_in_the_classroom_karen_mensing  8.90M  12.3G   143K
                how_the_language_you_speak_affects_your_thoughts  16.7M  12.4G   143K
                              how_life_came_to_land_tierney_thys  17.8M  12.4G   142K
    how_cosmic_rays_help_us_understand_the_universe_veronica_bin  16.4M  12.4G   141K
               inventing_the_american_presidency_kenneth_c_davis  9.96M  12.4G   140K
       silk_the_ancient_material_of_the_future_fiorenzo_omenetto  15.9M  12.4G   139K
    speech_acts_constative_and_performative_colleen_glenney_bogg  9.02M  12.4G   138K
           the_abc_s_of_gas_avogadro_boyle_charles_brian_bennett  6.01M  12.4G   137K
      a_trip_through_space_to_calculate_distance_heather_tunnell  6.01M  12.4G   137K
            why_you_will_fail_to_have_a_great_career_larry_smith  41.2M  12.5G   137K
             how_bees_help_plants_have_sex_fernanda_s_valdovinos  8.59M  12.5G   134K
                animation_basics_homemade_special_effects_ted_ed  10.4M  12.5G   134K
    the_surprising_and_invisible_signatures_of_sea_creatures_kak  19.3M  12.5G   133K
              euclid_s_puzzling_parallel_postulate_jeff_dekofsky  6.13M  12.5G   132K
     let_s_talk_about_sex_john_bohannon_and_black_label_movement  30.3M  12.5G   130K
           it_s_time_to_question_bio_engineering_paul_root_wolpe  29.3M  12.6G   130K
                  three_months_after_by_cristin_o_keefe_aptowicz  2.85M  12.6G   129K
                           printing_a_human_kidney_anthony_atala  39.3M  12.6G   126K
       rhythm_in_a_box_the_story_of_the_cajon_drum_paul_jennings  10.6M  12.6G   125K
                      greeting_the_world_in_peace_jackie_jenkins  9.34M  12.6G   124K
                        my_glacier_cave_discoveries_eddy_cartaya  16.7M  12.6G   123K
      how_farming_planted_seeds_for_the_internet_patricia_russac  6.56M  12.7G   122K
                   how_to_take_a_great_picture_carolina_molinari  4.93M  12.7G   122K
                           don_t_insist_on_english_patricia_ryan  16.4M  12.7G   122K
                  your_elusive_creative_genius_elizabeth_gilbert  40.2M  12.7G   121K
    string_theory_and_the_hidden_structures_of_the_universe_clif  15.7M  12.7G   120K
                                 tales_of_passion_isabel_allende  29.3M  12.8G   120K
     mysteries_of_vernacular_lady_jessica_oreck_and_rachael_teel  2.94M  12.8G   119K
    the_mysterious_workings_of_the_adolescent_brain_sarah_jayne_  31.1M  12.8G   116K
        want_to_be_happier_stay_in_the_moment_matt_killingsworth  18.3M  12.8G   115K
                                  cern_s_supercollider_brian_cox  26.8M  12.8G   115K
         could_comets_be_the_source_of_life_on_earth_justin_dowd  7.00M  12.8G   114K
    why_extremophiles_bode_well_for_life_beyond_earth_louisa_pre  7.56M  12.8G   112K
                       inside_a_cartoonist_s_world_liza_donnelly  12.4M  12.9G   112K
                  curiosity_discovery_and_gecko_feet_robert_full  13.7M  12.9G   111K
                           why_do_we_see_illusions_mark_changizi  15.5M  12.9G   111K
                       the_story_behind_your_glasses_eva_timothy  12.4M  12.9G   111K
        describing_the_invisible_properties_of_gas_brian_bennett  7.12M  12.9G   111K
     the_emergence_of_drama_as_a_literary_art_mindy_ploeckelmann  7.41M  12.9G   111K
       pavlovian_reactions_aren_t_just_for_dogs_benjamin_n_witts  12.0M  12.9G   110K
                     an_exercise_in_time_perception_matt_danzico  10.3M  12.9G   110K
               strange_answers_to_the_psychopath_test_jon_ronson  32.7M  13.0G   110K
     magical_metals_how_shape_memory_alloys_work_ainissa_ramirez  10.0M  13.0G   109K
          distant_time_and_the_hint_of_a_multiverse_sean_carroll  26.5M  13.0G   103K
                ted_invites_the_class_of_2020_to_give_a_ted_talk  3.54M  13.0G 100.0K
                       how_photography_connects_us_david_griffin  21.2M  13.0G  98.0K
                  distorting_madonna_in_medieval_art_james_earle  5.58M  13.0G  97.7K
        parasite_tales_the_jewel_wasp_s_zombie_slave_carl_zimmer  15.8M  13.1G  97.6K
                   science_can_answer_moral_questions_sam_harris  47.2M  13.1G  97.4K
                     does_racism_affect_how_you_vote_nate_silver  15.5M  13.1G  97.1K
                   actually_the_world_isn_t_flat_pankaj_ghemawat  41.9M  13.2G  95.6K
                          on_positive_psychology_martin_seligman  42.8M  13.2G  94.9K
                   pruney_fingers_a_gripping_story_mark_changizi  9.86M  13.2G  93.8K
                   capturing_authentic_narratives_michele_weldon  7.14M  13.2G  93.2K
                       see_yemen_through_my_eyes_nadia_al_sakkaf  26.1M  13.2G  93.1K
                        all_your_devices_can_be_hacked_avi_rubin  24.9M  13.3G  92.4K
    mysteries_of_vernacular_robot_jessica_oreck_and_rachael_teel  3.26M  13.3G  92.2K
                                a_tap_dancer_s_craft_andrew_nemr  13.4M  13.3G  91.7K
      dark_matter_how_does_it_explain_a_star_s_speed_don_lincoln  5.78M  13.3G  91.0K
                a_digital_reimagining_of_gettysburg_anne_knowles  15.6M  13.3G  90.7K
                               connected_but_alone_sherry_turkle  34.2M  13.3G  90.7K
       the_weird_wonderful_world_of_bioluminescence_edith_widder  20.8M  13.4G  90.6K
    defining_cyberwarfare_in_hopes_of_preventing_it_daniel_garri  7.67M  13.4G  90.3K
                        the_mystery_of_chronic_pain_elliot_krane  16.0M  13.4G  89.8K
                           math_class_needs_a_makeover_dan_meyer  18.7M  13.4G  89.4K
                   what_s_wrong_with_our_food_system_birke_baehr  8.37M  13.4G  88.9K
          how_two_decisions_led_me_to_olympic_glory_steve_mesler  9.62M  13.4G  88.5K
                  the_networked_beauty_of_forests_suzanne_simard  22.0M  13.4G  88.5K
    put_those_smartphones_away_great_tips_for_making_your_job_in  19.0M  13.5G  88.4K
                            underwater_astonishments_david_gallo  13.3M  13.5G  87.6K
                          the_power_of_vulnerability_brene_brown  32.3M  13.5G  87.6K
            the_neurons_that_shaped_civilization_vs_ramachandran  13.9M  13.5G  87.3K
                              sending_a_sundial_to_mars_bill_nye  13.0M  13.5G  87.1K
                     taking_imagination_seriously_janet_echelman  27.4M  13.5G  86.6K
                    how_great_leaders_inspire_action_simon_sinek  55.7M  13.6G  86.4K
                                the_future_of_lying_jeff_hancock  54.2M  13.7G  85.8K
       a_call_to_invention_diy_speaker_edition_william_gurstelle  21.0M  13.7G  83.4K
               let_s_use_video_to_reinvent_education_salman_khan  36.3M  13.7G  82.9K
                                making_a_ted_ed_lesson_animation  13.2M  13.7G  82.0K
          biofuels_and_bioprospecting_for_beginners_craig_a_kohn  9.67M  13.7G  81.3K
                          on_exploring_the_oceans_robert_ballard  32.3M  13.8G  80.1K
                    how_to_stop_being_bored_and_start_being_bold  29.8M  13.8G  79.7K
                    america_s_native_prisoners_of_war_aaron_huey  24.2M  13.8G  79.3K
               a_teen_just_trying_to_figure_it_out_tavi_gevinson  13.2M  13.8G  78.8K
          gridiron_physics_scalars_and_vectors_michelle_buchanan  10.8M  13.8G  78.6K
                measuring_what_makes_life_worthwhile_chip_conley  30.8M  13.9G  77.7K
                   hiv_and_flu_the_vaccine_strategy_seth_berkley  48.5M  13.9G  77.2K
    mysteries_of_vernacular_yankee_jessica_oreck_and_rachael_tee  2.83M  13.9G  74.1K
    conserving_our_spectacular_vulnerable_coral_reefs_joshua_dre  7.22M  13.9G  73.2K
                             how_to_track_a_tornado_karen_kosiba  14.1M  13.9G  73.2K
                             on_spaghetti_sauce_malcolm_gladwell  40.2M  14.0G  72.7K
                        questioning_the_universe_stephen_hawking  19.1M  14.0G  72.6K
     mysteries_of_vernacular_zero_jessica_oreck_and_rachael_teel  2.82M  14.0G  72.3K
                               our_loss_of_wisdom_barry_schwartz  63.2M  14.1G  72.1K
              breaking_the_illusion_of_skin_color_nina_jablonski  26.8M  14.1G  71.6K
                     why_work_doesn_t_happen_at_work_jason_fried  24.0M  14.1G  69.4K
             dance_vs_powerpoint_a_modest_proposal_john_bohannon  31.7M  14.1G  69.3K
                      deep_sea_diving_in_a_wheelchair_sue_austin  26.6M  14.2G  68.5K
                   the_linguistic_genius_of_babies_patricia_kuhl  15.9M  14.2G  67.5K
         how_to_find_the_true_face_of_leonardo_siegfried_woldhek  6.53M  14.2G  67.1K
              we_need_to_talk_about_an_injustice_bryan_stevenson  41.9M  14.2G  66.8K
                        your_genes_are_not_your_fate_dean_ornish  4.86M  14.2G  66.7K
       dissecting_botticelli_s_adoration_of_the_magi_james_earle  7.88M  14.2G  66.5K
                             historical_role_models_amy_bissetta  5.19M  14.3G  66.1K
               what_makes_us_feel_good_about_our_work_dan_ariely  31.8M  14.3G  65.8K
                                i_listen_to_color_neil_harbisson  24.6M  14.3G  65.5K
                     how_curiosity_got_us_to_mars_bobak_ferdowsi  12.3M  14.3G  65.4K
          phenology_and_nature_s_shifting_rhythms_regina_brinker  6.93M  14.3G  64.6K
                         the_sweaty_teacher_s_lament_justin_lamb  9.95M  14.3G  64.4K
                                  listening_to_shame_brene_brown  40.4M  14.4G  64.1K
                      mysteries_of_vernacular_clue_jessica_oreck  3.72M  14.4G  63.3K
    mysteries_of_vernacular_ukulele_jessica_oreck_and_rachael_te  2.69M  14.4G  63.3K
                     stories_legacies_of_who_we_are_awele_makeba  20.8M  14.4G  63.2K
                             folding_way_new_origami_robert_lang  30.5M  14.4G  62.4K
                        making_a_ted_ed_lesson_animating_zombies  9.24M  14.4G  61.9K
                             erin_mckean_the_joy_of_lexicography  32.7M  14.5G  61.6K
                  how_to_make_work_life_balance_work_nigel_marsh  21.7M  14.5G  61.5K
     the_family_structure_of_elephants_caitlin_o_connell_rodwell  16.6M  14.5G  61.1K
    self_assembly_the_power_of_organizing_the_unorganized_skylar  6.34M  14.5G  60.3K
             3_things_i_learned_while_my_plane_crashed_ric_elias  9.01M  14.5G  58.9K
                               make_robots_smarter_ayanna_howard  19.2M  14.5G  58.0K
                    the_danger_of_science_denial_michael_specter  36.6M  14.6G  57.9K
    how_giant_sea_creatures_eat_tiny_sea_creatures_kelly_benoit_  13.0M  14.6G  57.9K
                  visualizing_the_world_s_twitter_data_jer_thorp  14.6M  14.6G  57.8K
                                why_is_x_the_unknown_terry_moore  6.43M  14.6G  57.8K
    mysteries_of_vernacular_quarantine_jessica_oreck_and_rachael  3.45M  14.6G  57.4K
                                  adhd_finding_what_works_for_me  26.0M  14.6G  57.0K
    could_your_language_affect_your_ability_to_save_money_keith_  25.0M  14.7G  56.7K
       is_the_obesity_crisis_hiding_a_bigger_problem_peter_attia  38.9M  14.7G  56.6K
                  tracking_grizzly_bears_from_space_david_laskin  11.5M  14.7G  56.4K
              learning_from_past_presidents_doris_kearns_goodwin  29.6M  14.7G  56.3K
                               a_plant_s_eye_view_michael_pollan  45.5M  14.8G  55.6K
                         the_human_and_the_honeybee_dino_martins  13.5M  14.8G  55.0K
         early_forensics_and_crime_solving_chemists_deborah_blum  15.9M  14.8G  54.8K
                           less_stuff_more_happiness_graham_hill  8.50M  14.8G  54.5K
                  mysteries_of_vernacular_assassin_jessica_oreck  3.34M  14.8G  54.4K
    how_one_teenager_unearthed_baseball_s_untold_history_cam_per  13.5M  14.8G  53.4K
    how_whales_breathe_communicate_and_fart_with_their_faces_joy  16.1M  14.9G  53.3K
               the_pattern_behind_self_deception_michael_shermer  32.1M  14.9G  53.3K
                how_architecture_helped_music_evolve_david_byrne  31.4M  14.9G  53.0K
                   sublimation_mit_digital_lab_techniques_manual  8.96M  14.9G  52.9K
                             averting_the_climate_crisis_al_gore  48.8M  15.0G  52.7K
    mysteries_of_vernacular_bewilder_jessica_oreck_and_rachael_t  3.08M  15.0G  52.6K
            how_art_gives_shape_to_cultural_change_thelma_golden  19.5M  15.0G  52.3K
                time_lapse_proof_of_extreme_ice_loss_james_balog  45.5M  15.0G  51.7K
    mysteries_of_vernacular_earwig_jessica_oreck_and_rachael_tee  3.50M  15.0G  51.7K
                                              is_equality_enough  14.0M  15.1G  51.6K
                           are_video_games_actually_good_for_you  13.5M  15.1G  51.4K
           visualizing_hidden_worlds_inside_your_body_dee_breger  12.0M  15.1G  51.0K
                          a_40_year_plan_for_energy_amory_lovins  41.3M  15.1G  50.2K
                          the_hidden_power_of_smiling_ron_gutman  15.4M  15.1G  49.6K
          why_i_must_speak_out_about_climate_change_james_hansen  28.7M  15.2G  49.6K
                         different_ways_of_knowing_daniel_tammet  16.6M  15.2G  49.2K
                              earth_s_mass_extinction_peter_ward  29.1M  15.2G  49.1K
                                        true_success_john_wooden  53.9M  15.3G  49.0K
            how_state_budgets_are_breaking_us_schools_bill_gates  18.3M  15.3G  48.8K
                               click_your_fortune_episode_1_demo  5.03M  15.3G  47.1K
                                 the_bottom_billion_paul_collier  37.6M  15.3G  46.9K
    mysteries_of_vernacular_gorgeous_jessica_oreck_and_rachael_t  3.17M  15.3G  46.8K
            making_a_ted_ed_lesson_synesthesia_and_playing_cards  9.15M  15.3G  46.7K
                                     the_birth_of_a_word_deb_roy  43.2M  15.4G  46.6K
              high_altitude_wind_energy_from_kites_saul_griffith  11.2M  15.4G  46.6K
    ted_ed_clubs_celebrating_and_amplifying_student_voices_aroun  5.79M  15.4G  46.5K
    what_we_learned_from_5_million_books_erez_lieberman_aiden_an  21.7M  15.4G  45.6K
                 toy_tiles_that_talk_to_each_other_david_merrill  17.9M  15.4G  45.6K
                                 our_buggy_moral_code_dan_ariely  39.5M  15.5G  45.4K
                     mysteries_of_vernacular_noise_jessica_oreck  3.50M  15.5G  45.4K
    the_shape_shifting_future_of_the_mobile_phone_fabian_hemmert  8.23M  15.5G  44.4K
                  are_we_ready_for_neo_evolution_harvey_fineberg  28.5M  15.5G  44.4K
                           the_post_crisis_consumer_john_gerzema  24.9M  15.5G  44.3K
                              the_art_of_choosing_sheena_iyengar  40.0M  15.6G  43.9K
                               why_videos_go_viral_kevin_allocca  13.9M  15.6G  43.4K
                        beware_online_filter_bubbles_eli_pariser  16.3M  15.6G  43.4K
               creative_houses_from_reclaimed_stuff_dan_phillips  33.1M  15.6G  43.0K
                     mysteries_of_vernacular_pants_jessica_oreck  3.38M  15.6G  42.7K
              yup_i_built_a_nuclear_fusion_reactor_taylor_wilson  8.14M  15.6G  42.7K
                         moral_behavior_in_animals_frans_de_waal  36.4M  15.7G  42.2K
                         pop_an_ollie_and_innovate_rodney_mullen  48.2M  15.7G  42.1K
          making_a_ted_ed_lesson_two_ways_to_animate_slam_poetry  15.0M  15.7G  41.5K
       toward_a_new_understanding_of_mental_illness_thomas_insel  22.1M  15.8G  41.4K
                  shedding_light_on_dark_matter_patricia_burchat  26.7M  15.8G  41.4K
                           redefining_the_dictionary_erin_mckean  29.9M  15.8G  41.2K
                           a_new_way_to_diagnose_autism_ami_klin  37.7M  15.9G  40.6K
                       planning_for_the_end_of_oil_richard_sears  20.1M  15.9G  40.3K
                        seeing_a_sustainable_future_alex_steffen  15.3M  15.9G  40.3K
    mysteries_of_vernacular_dynamite_jessica_oreck_and_rachael_t  3.53M  15.9G  40.0K
    mysteries_of_vernacular_x_ray_jessica_oreck_and_rachael_teel  2.58M  15.9G  39.6K
                       building_a_culture_of_success_mark_wilson  15.1M  15.9G  39.6K
                    mysteries_of_vernacular_tuxedo_jessica_oreck  3.59M  15.9G  39.5K
                       how_i_learned_to_organize_my_scatterbrain  30.4M  15.9G  39.4K
              on_being_a_woman_and_a_diplomat_madeleine_albright  28.9M  16.0G  38.8K
                the_surprising_science_of_happiness_nancy_etcoff  24.1M  16.0G  38.7K
           the_search_for_other_earth_like_planets_olivier_guyon  13.7M  16.0G  38.6K
                              the_3_a_s_of_awesome_neil_pasricha  41.3M  16.1G  38.5K
       how_economic_inequality_harms_societies_richard_wilkinson  31.0M  16.1G  38.1K
                 mysteries_of_vernacular_miniature_jessica_oreck  3.84M  16.1G  38.0K
                                   on_being_wrong_kathryn_schulz  35.0M  16.1G  37.9K
          medicine_s_future_there_s_an_app_for_that_daniel_kraft  25.1M  16.1G  37.2K
        detention_or_eco_club_choosing_your_future_juan_martinez  9.35M  16.2G  37.0K
             fractals_and_the_art_of_roughness_benoit_mandelbrot  34.0M  16.2G  36.6K
                       a_warm_embrace_that_saves_lives_jane_chen  8.86M  16.2G  36.3K
                     how_to_learn_from_mistakes_diana_laufenberg  21.9M  16.2G  36.3K
                        how_to_restore_a_rainforest_willie_smits  40.2M  16.3G  36.2K
                       how_i_fell_in_love_with_a_fish_dan_barber  39.0M  16.3G  36.1K
                        are_we_born_to_run_christopher_mcdougall  45.3M  16.3G  35.7K
    mysteries_of_vernacular_window_jessica_oreck_and_rachael_tee  3.31M  16.3G  35.5K
                the_lost_art_of_democratic_debate_michael_sandel  54.1M  16.4G  35.1K
    mysteries_of_vernacular_sarcophagus_jessica_oreck_and_rachae  2.57M  16.4G  35.0K
                         navigating_our_global_future_ian_goldin  12.2M  16.4G  34.9K
    mysteries_of_vernacular_venom_jessica_oreck_and_rachael_teel  3.18M  16.4G  34.7K
    mysteries_of_vernacular_keister_jessica_oreck_and_rachael_te  2.86M  16.4G  34.6K
                              the_security_mirage_bruce_schneier  40.7M  16.5G  34.2K
                mysteries_of_vernacular_inaugurate_jessica_oreck  3.45M  16.5G  34.1K
                     txtng_is_killing_language_jk_john_mcwhorter  27.1M  16.5G  34.0K
                     the_other_inconvenient_truth_jonathan_foley  29.5M  16.5G  33.7K
            every_city_needs_healthy_honey_bees_noah_wilson_rich  28.1M  16.5G  33.5K
                 the_mathematics_of_history_jean_baptiste_michel  7.24M  16.5G  33.4K
                cleaning_our_oceans_a_big_plan_for_a_big_problem  27.3M  16.6G  33.1K
                           my_seven_species_of_robot_dennis_hong  30.5M  16.6G  32.8K
                    digging_for_humanity_s_origins_louise_leakey  31.1M  16.6G  32.8K
                                       exciting_news_from_ted_ed  5.13M  16.6G  32.7K
    mysteries_of_vernacular_fizzle_jessica_oreck_and_rachael_tee  2.65M  16.6G  32.7K
                    bring_ted_to_the_classroom_with_ted_ed_clubs  2.33M  16.6G  32.5K
               dare_to_educate_afghan_girls_shabana_basij_rasikh  21.9M  16.7G  32.4K
                  building_the_seed_cathedral_thomas_heatherwick  31.9M  16.7G  32.2K
     mysteries_of_vernacular_jade_jessica_oreck_and_rachael_teel  3.39M  16.7G  32.2K
                   hey_science_teachers_make_it_fun_tyler_dewitt  28.3M  16.7G  31.7K
                 a_rosetta_stone_for_the_indus_script_rajesh_rao  27.9M  16.8G  31.6K
                      why_eyewitnesses_get_it_wrong_scott_fraser  43.1M  16.8G  31.5K
                  ted_prize_wish_protect_our_oceans_sylvia_earle  55.7M  16.9G  31.4K
                                              math_is_everywhere  8.18M  16.9G  31.4K
                   faith_versus_tradition_in_islam_mustafa_akyol  27.2M  16.9G  31.3K
                      symmetry_reality_s_riddle_marcus_du_sautoy  40.1M  16.9G  31.2K
                              how_to_use_a_paper_towel_joe_smith  11.2M  16.9G  31.1K
                               your_brain_on_improv_charles_limb  29.6M  17.0G  30.2K
           the_quest_to_understand_consciousness_antonio_damasio  31.8M  17.0G  30.1K
                    mysteries_of_vernacular_hearse_jessica_oreck  3.73M  17.0G  30.0K
                                            meet_julia_delmedico  5.45M  17.0G  29.9K
                       feats_of_memory_anyone_can_do_joshua_foer  33.5M  17.0G  29.9K
               building_a_museum_of_museums_on_the_web_amit_sood  9.86M  17.0G  29.6K
    why_domestic_violence_victims_don_t_leave_leslie_morgan_stei  33.8M  17.1G  28.9K
                  high_tech_art_with_a_sense_of_humor_aparna_rao  12.7M  17.1G  28.6K
       ashton_cofer_a_young_inventor_s_plan_to_recycle_styrofoam  11.2M  17.1G  28.5K
                 404_the_story_of_a_page_not_found_renny_gleeson  7.71M  17.1G  28.4K
                                       announcing_ted_ed_espanol  2.06M  17.1G  27.8K
               healthier_men_one_moustache_at_a_time_adam_garone  47.6M  17.2G  27.6K
                 behind_the_great_firewall_of_china_michael_anti  35.3M  17.2G  27.5K
                   the_beautiful_math_of_coral_margaret_wertheim  28.2M  17.2G  27.2K
              will_our_kids_be_a_different_species_juan_enriquez  27.3M  17.2G  26.9K
              how_will_ted_ed_celebrate_its_1000000th_subscriber  2.80M  17.3G  26.4K
                              the_demise_of_guys_philip_zimbardo  8.43M  17.3G  26.4K
                                 the_art_of_asking_amanda_palmer  29.5M  17.3G  26.3K
               the_business_logic_of_sustainability_ray_anderson  33.2M  17.3G  26.3K
                  building_a_dinosaur_from_a_chicken_jack_horner  25.4M  17.3G  26.1K
               what_you_don_t_know_about_marriage_jenna_mccarthy  18.1M  17.4G  25.8K
                       making_a_ted_ed_lesson_concept_and_design  9.81M  17.4G  25.7K
                        the_good_news_of_the_decade_hans_rosling  29.8M  17.4G  25.6K
           imaging_at_a_trillion_frames_per_second_ramesh_raskar  20.9M  17.4G  25.6K
       your_brain_is_more_than_a_bag_of_chemicals_david_anderson  29.0M  17.5G  25.3K
                        the_myth_of_the_gay_agenda_lz_granderson  44.1M  17.5G  25.3K
                                              meet_melissa_perez  5.01M  17.5G  25.2K
            4_lessons_from_robots_about_being_human_ken_goldberg  29.5M  17.5G  23.9K
                      why_we_need_to_go_back_to_mars_joel_levine  27.5M  17.6G  23.8K
                                do_the_green_thing_andy_hobsbawm  6.83M  17.6G  23.7K
              the_el_sistema_music_revolution_jose_antonio_abreu  36.7M  17.6G  23.6K
                  ladies_and_gentlemen_the_hobart_shakespeareans  28.0M  17.6G  23.6K
            music_and_emotion_through_time_michael_tilson_thomas  38.8M  17.7G  23.2K
                          the_real_goal_equal_pay_for_equal_play  16.5M  17.7G  23.0K
                             the_walk_from_no_to_yes_william_ury  36.8M  17.7G  22.9K
                                      doodlers_unite_sunni_brown  10.0M  17.7G  22.8K
                                 how_to_spot_a_liar_pamela_meyer  31.3M  17.8G  22.8K
                        retrofitting_suburbia_ellen_dunham_jones  35.5M  17.8G  22.8K
                                                meet_shayna_cody  3.82M  17.8G  22.5K
                                 losing_everything_david_hoffman  11.2M  17.8G  22.4K
             the_hidden_beauty_of_pollination_louie_schwartzberg  24.1M  17.8G  22.1K
                              archeology_from_space_sarah_parcak  9.71M  17.8G  21.7K
             let_s_raise_kids_to_be_entrepreneurs_cameron_herold  34.9M  17.9G  21.2K
                               how_a_fly_flies_michael_dickinson  26.6M  17.9G  21.0K
        making_sense_of_a_visible_quantum_object_aaron_o_connell  15.7M  17.9G  21.0K
                        the_sound_the_universe_makes_janna_levin  36.3M  17.9G  20.9K
                            a_light_switch_for_neurons_ed_boyden  42.0M  18.0G  20.7K
                              what_do_babies_think_alison_gopnik  38.1M  18.0G  20.5K
    how_mr_condom_made_thailand_a_better_place_mechai_viravaidya  24.8M  18.1G  20.5K
                      a_future_beyond_traffic_gridlock_bill_ford  29.2M  18.1G  20.3K
                                   praising_slowness_carl_honore  60.5M  18.1G  20.3K
                    overcoming_the_scientific_divide_aaron_reedy  13.3M  18.2G  19.9K
    image_recognition_that_triggers_augmented_reality_matt_mills  21.2M  18.2G  19.9K
                     how_benjamin_button_got_his_face_ed_ulbrich  38.8M  18.2G  19.6K
                          teachers_need_real_feedback_bill_gates  24.7M  18.2G  19.5K
                   could_a_saturn_moon_harbor_life_carolyn_porco  7.68M  18.2G  19.5K
                   what_s_so_funny_about_mental_illness_ruby_wax  27.3M  18.3G  19.3K
                                      social_animal_david_brooks  35.9M  18.3G  19.3K
                   a_new_ecosystem_for_electric_cars_shai_agassi  36.8M  18.3G  19.2K
                      tour_the_solar_system_from_home_jon_nguyen  12.3M  18.4G  19.2K
                 four_principles_for_the_open_world_don_tapscott  42.3M  18.4G  18.9K
                       supercharged_motorcycle_design_yves_behar  4.62M  18.4G  18.6K
                  the_beautiful_tricks_of_flowers_jonathan_drori  21.6M  18.4G  18.4K
                               battling_bad_science_ben_goldacre  30.4M  18.4G  18.0K
              a_tale_of_mental_illness_from_the_inside_elyn_saks  34.2M  18.5G  17.9K
             lessons_from_fashion_s_free_culture_johanna_blakley  20.7M  18.5G  17.5K
          from_mach_20_glider_to_humming_bird_drone_regina_dugan  44.8M  18.5G  17.3K
    a_navy_admiral_s_thoughts_on_global_security_james_stavridis  37.4M  18.6G  17.3K
    cheese_dogs_and_a_pill_to_kill_mosquitoes_and_end_malaria_ba  22.9M  18.6G  17.2K
                                  the_earth_is_full_paul_gilding  26.8M  18.6G  17.1K
                         making_a_ted_ed_lesson_creative_process  10.3M  18.6G  17.1K
                     how_poachers_became_caretakers_john_kasaona  27.9M  18.7G  17.0K
                             dare_to_disagree_margaret_heffernan  21.2M  18.7G  16.8K
                           unintended_consequences_edward_tenner  24.9M  18.7G  16.6K
                a_saudi_woman_who_dared_to_drive_manal_al_sharif  33.2M  18.7G  16.5K
    why_libya_s_revolution_didn_t_work_and_what_might_zahra_lang  28.5M  18.8G  16.5K
          distant_time_and_the_hint_of_a_multiverse_sean_carroll  26.5M  18.8G  16.4K
                      making_a_car_for_blind_drivers_dennis_hong  20.6M  18.8G  16.4K
                                     atheism_2_0_alain_de_botton  46.6M  18.9G  16.4K
                          why_global_jihad_is_losing_bobby_ghosh  30.8M  18.9G  16.0K
                                   tribal_leadership_david_logan  34.7M  18.9G  16.0K
                                 the_evolution_of_the_human_head  13.8M  18.9G  16.0K
               the_true_power_of_the_performing_arts_ben_cameron  27.2M  19.0G  15.7K
             the_rise_of_human_computer_cooperation_shyam_sankar  20.1M  19.0G  15.6K
                 we_need_a_moral_operating_system_damon_horowitz  43.7M  19.0G  15.6K
                         let_s_simplify_legal_jargon_alan_siegel  9.12M  19.0G  15.4K
             a_cinematic_journey_through_visual_effects_don_levy  20.5M  19.1G  15.3K
            your_online_life_permanent_as_a_tattoo_juan_enriquez  8.77M  19.1G  15.3K
              the_game_layer_on_top_of_the_world_seth_priebatsch  22.2M  19.1G  15.2K
    what_doctors_don_t_know_about_the_drugs_they_prescribe_ben_g  29.1M  19.1G  15.1K
                natural_pest_control_using_bugs_shimon_steinberg  29.6M  19.1G  15.1K
                                             meet_shahruz_ghaemi  4.58M  19.2G  15.1K
            women_should_represent_women_in_media_megan_kamerick  21.3M  19.2G  15.0K
                              why_democracy_matters_rory_stewart  24.9M  19.2G  15.0K
                                           redefining_the_f_word  13.2M  19.2G  14.9K
         the_moral_dangers_of_non_lethal_weapons_stephen_coleman  52.0M  19.3G  14.8K
               the_science_behind_a_climate_headline_rachel_pike  7.32M  19.3G  14.7K
             protecting_the_brain_against_concussion_kim_gorgens  18.6M  19.3G  14.5K
       how_youtube_thinks_about_copyright_margaret_gould_stewart  11.6M  19.3G  14.0K
                     the_emergence_of_4d_printing_skylar_tibbits  15.8M  19.3G  13.8K
          how_arduino_is_open_sourcing_imagination_massimo_banzi  28.4M  19.3G  13.3K
                how_to_use_experts_and_when_not_to_noreena_hertz  37.2M  19.4G  13.2K
                               religions_and_babies_hans_rosling  22.2M  19.4G  13.1K
                   the_generation_that_s_remaking_china_yang_lan  33.6M  19.4G  13.1K
                            ted_ed_clubs_presents_ted_ed_weekend  8.88M  19.4G  13.0K
                            trust_morality_and_oxytocin_paul_zak  37.0M  19.5G  12.7K
              how_i_m_preparing_to_get_alzheimer_s_alanna_shaikh  12.8M  19.5G  12.2K
                        how_to_solve_traffic_jams_jonas_eliasson  16.4M  19.5G  12.1K
                                           be_you_ty_over_beauty  21.9M  19.5G  11.8K
                       inside_an_antarctic_time_machine_lee_hotz  14.9M  19.5G  11.8K
          the_beautiful_nano_details_of_our_world_gary_greenberg  18.9M  19.6G  11.8K
                 using_unanswered_questions_to_teach_john_gensic  8.99M  19.6G  11.8K
                a_global_culture_to_fight_extremism_maajid_nawaz  43.1M  19.6G  11.3K
                    a_radical_experiment_in_empathy_sam_richards  31.9M  19.6G  11.2K
         want_to_help_someone_shut_up_and_listen_ernesto_sirolli  36.4M  19.7G  11.1K
                 the_journey_across_the_high_wire_philippe_petit  32.7M  19.7G  11.1K
                               greening_the_ghetto_majora_carter  50.5M  19.8G  11.1K
                      gaming_for_understanding_brenda_brathwaite  15.4M  19.8G  11.0K
                toward_a_science_of_simplicity_george_whitesides  34.4M  19.8G  11.0K
          how_can_technology_transform_the_human_body_lucy_mcrae  8.98M  19.8G  11.0K
                        are_droids_taking_our_jobs_andrew_mcafee  28.5M  19.8G  10.8K
                       the_real_reason_for_brains_daniel_wolpert  34.9M  19.9G  10.6K
                             can_we_domesticate_germs_paul_ewald  29.9M  19.9G  10.5K
                                   the_optimism_bias_tali_sharot  30.9M  19.9G  10.4K
      the_key_to_growth_race_with_the_machines_erik_brynjolfsson  19.7M  20.0G  10.4K
                    superhero_training_what_you_can_do_right_now  31.8M  20.0G  10.3K
            our_failing_schools_enough_is_enough_geoffrey_canada  50.1M  20.0G  10.3K
                my_backyard_got_way_cooler_when_i_added_a_dragon  13.3M  20.0G  10.2K
                animating_a_photo_real_digital_face_paul_debevec  10.2M  20.1G  10.0K
                               click_your_fortune_episode_2_demo  4.97M  20.1G  9.98K
                                  a_map_of_the_brain_allan_jones  35.0M  20.1G  9.91K
                    learning_from_a_barefoot_movement_bunker_roy  37.1M  20.1G  9.79K
                  agile_programming_for_your_family_bruce_feiler  38.5M  20.2G  9.69K
                           the_equation_for_reaching_your_dreams  25.3M  20.2G  9.64K
                       ancient_wonders_captured_in_3d_ben_kacyra  29.8M  20.2G  9.46K
      facing_the_real_me_looking_in_the_mirror_with_natural_hair  28.9M  20.3G  9.45K
    a_critical_examination_of_the_technology_in_our_lives_kevin_  12.7M  20.3G  9.37K
                         reinventing_the_encyclopedia_game_rives  24.2M  20.3G  9.33K
      building_a_theater_that_remakes_itself_joshua_prince_ramus  30.5M  20.3G  9.09K
               sex_needs_a_new_metaphor_here_s_one_al_vernacchio  13.8M  20.3G  9.05K
                     how_we_ll_stop_polio_for_good_bruce_aylward  38.7M  20.4G  8.95K
                                   hire_the_hackers_misha_glenny  41.5M  20.4G  8.93K
                       perspective_is_everything_rory_sutherland  36.0M  20.4G  8.80K
                       the_secret_of_the_bat_genome_emma_teeling  32.3M  20.5G  8.64K
          meet_global_corruption_s_hidden_players_charmian_gooch  31.3M  20.5G  8.50K
                         what_is_the_internet_really_andrew_blum  17.1M  20.5G  8.48K
                            a_giant_bubble_for_debate_liz_diller  18.5M  20.5G  8.45K
                       the_4_commandments_of_cities_eduardo_paes  22.6M  20.6G  8.42K
                       one_way_to_create_a_more_inclusive_school  16.7M  20.6G  8.22K
                        we_need_better_drugs_now_francis_collins  25.9M  20.6G  8.16K
                         trusting_the_ensemble_charles_hazlewood  52.0M  20.7G  8.14K
                artificial_justice_would_robots_make_good_judges  14.1M  20.7G  8.12K
                    what_fear_can_teach_us_karen_thompson_walker  25.4M  20.7G  8.11K
         what_we_re_learning_from_online_education_daphne_koller  40.9M  20.7G  7.91K
              what_we_re_learning_from_5000_brains_read_montague  26.2M  20.8G  7.91K
        weaving_narratives_in_museum_galleries_thomas_p_campbell  34.8M  20.8G  7.91K
                      mining_minerals_from_seawater_damian_palin  4.76M  20.8G  7.77K
              how_poachers_became_caretakers_john_kasaona_glitch  28.4M  20.8G  7.64K
                            shape_shifting_dinosaurs_jack_horner  36.1M  20.9G  7.35K
                           texting_that_saves_lives_nancy_lublin  12.3M  20.9G  7.30K
                               click_your_fortune_episode_3_demo  5.18M  20.9G  7.29K
              obesity_hunger_1_global_food_issue_ellen_gustafson  15.4M  20.9G  7.16K
                 how_your_mom_s_advice_could_save_the_human_race  23.3M  20.9G  7.11K
             a_broken_body_isn_t_a_broken_person_janine_shepherd  34.8M  21.0G  7.08K
           the_case_for_collaborative_consumption_rachel_botsman  29.1M  21.0G  6.97K
              ultrasound_surgery_healing_without_cuts_yoav_medan  30.7M  21.0G  6.94K
                   how_to_defend_earth_from_asteroids_phil_plait  22.7M  21.0G  6.94K
                          let_s_teach_kids_to_code_mitch_resnick  29.1M  21.1G  6.92K
                 a_whistleblower_you_haven_t_heard_geert_chatrou  21.9M  21.1G  6.92K
                               a_doctor_s_touch_abraham_verghese  38.3M  21.1G  6.88K
                       how_we_found_the_giant_squid_edith_widder  15.2M  21.1G  6.76K
                      a_plane_you_can_drive_anna_mracek_dietrich  19.5M  21.2G  6.75K
                   a_civil_response_to_violence_emiliano_salinas  20.4M  21.2G  6.66K
         let_s_transform_energy_with_natural_gas_t_boone_pickens  34.6M  21.2G  6.65K
                    pool_medical_patents_save_lives_ellen_t_hoen  18.6M  21.2G  6.63K
                             how_to_buy_happiness_michael_norton  17.8M  21.2G  6.61K
                          re_examining_the_remix_lawrence_lessig  28.9M  21.3G  6.58K
    what_nonprofits_can_learn_from_coca_cola_melinda_french_gate  33.8M  21.3G  6.50K
                                kids_need_structure_colin_powell  33.4M  21.3G  6.48K
               a_mini_robot_powered_by_your_phone_keller_rinaudo  12.0M  21.3G  6.42K
                             meet_the_water_canary_sonaar_luthra  5.73M  21.4G  6.40K
           the_future_race_car_150mph_and_no_driver_chris_gerdes  29.8M  21.4G  6.30K
         a_universal_translator_for_surgeons_steven_schwaitzberg  19.3M  21.4G  6.27K
                   a_vision_of_crimes_in_the_future_marc_goodman  20.6M  21.4G  6.25K
     how_do_you_save_a_shark_you_know_nothing_about_simon_berrow  35.7M  21.5G  6.17K
        let_s_put_birth_control_back_on_the_agenda_melinda_gates  55.2M  21.5G  6.04K
             the_good_news_on_poverty_yes_there_s_good_news_bono  24.9M  21.5G  5.96K
               what_we_learn_before_we_re_born_annie_murphy_paul  21.3M  21.6G  5.95K
      sometimes_it_s_good_to_give_up_the_driver_s_seat_baba_shiv  24.8M  21.6G  5.89K
    unlock_the_intelligence_passion_greatness_of_girls_leymah_gb  44.7M  21.6G  5.81K
                        1000_tedtalks_6_words_sebastian_wernicke  13.3M  21.6G  5.75K
                         a_prosthetic_arm_that_feels_todd_kuiken  38.2M  21.7G  5.75K
                      my_friend_richard_feynman_leonard_susskind  27.6M  21.7G  5.64K
                   using_nature_to_grow_batteries_angela_belcher  19.7M  21.7G  5.51K
            experiments_that_hint_of_longer_lives_cynthia_kenyon  31.1M  21.8G  5.51K
             could_the_sun_be_good_for_your_heart_richard_weller  23.7M  21.8G  5.45K
                  energy_from_floating_algae_pods_jonathan_trent  30.6M  21.8G  5.41K
                 a_father_daughter_dance_in_prison_angela_patton  22.3M  21.8G  5.37K
                          crowdsource_your_health_lucien_engelen  14.6M  21.8G  5.35K
                              before_i_die_i_want_to_candy_chang  11.3M  21.9G  5.31K
                                         where_is_home_pico_iyer  31.2M  21.9G  5.30K
                       the_dance_of_the_dung_beetle_marcus_byrne  35.9M  21.9G  5.28K
                      lessons_from_death_row_inmates_david_r_dow  32.2M  21.9G  5.19K
                                    a_future_lit_by_solar_energy  34.4M  22.0G  5.18K
             mental_health_for_all_by_involving_all_vikram_patel  32.5M  22.0G  5.11K
                  how_healthy_living_nearly_killed_me_a_j_jacobs  14.8M  22.0G  5.05K
                            how_do_we_heal_medicine_atul_gawande  33.9M  22.1G  5.02K
    what_s_a_snollygoster_a_short_lesson_in_political_speak_mark  15.6M  22.1G  4.99K
                                a_child_of_the_state_lemn_sissay  29.0M  22.1G  4.99K
    science_is_for_everyone_kids_included_beau_lotto_and_amy_o_t  37.9M  22.1G  4.91K
                          how_to_topple_a_dictator_srdja_popovic  37.9M  22.2G  4.86K
                  let_s_prepare_for_our_new_climate_vicki_arroyo  21.3M  22.2G  4.86K
    parkinson_s_depression_and_the_switch_that_might_turn_them_o  24.7M  22.2G  4.66K
          gaming_to_re_engage_boys_in_learning_ali_carr_chellman  24.5M  22.2G  4.60K
                  neuroscience_game_theory_monkeys_colin_camerer  21.7M  22.3G  4.56K
                    the_voice_of_the_natural_world_bernie_krause  34.1M  22.3G  4.48K
        telling_my_whole_story_when_many_cultures_make_one_voice  38.6M  22.3G  4.47K
    the_single_biggest_health_threat_women_face_noel_bairey_merz  31.5M  22.4G  4.45K
    a_choreographer_s_creative_process_in_real_time_wayne_mcgreg  43.7M  22.4G  4.44K
    we_the_people_and_the_republic_we_must_reclaim_lawrence_less  34.1M  22.4G  4.40K
            michael_green_why_we_should_build_wooden_skyscrapers  23.7M  22.5G  4.38K
                           how_to_expose_the_corrupt_peter_eigen  26.9M  22.5G  4.38K
                      inside_the_egyptian_revolution_wael_ghonim  26.8M  22.5G  4.37K
       a_clean_energy_proposal_race_to_the_top_jennifer_granholm  27.2M  22.5G  4.37K
         how_i_taught_rats_to_sniff_out_land_mines_bart_weetjens  22.5M  22.6G  4.26K
                 the_shared_experience_of_absurdity_charlie_todd  32.2M  22.6G  4.23K
    could_tissue_engineering_mean_personalized_medicine_nina_tan  10.3M  22.6G  4.19K
                                     my_immigration_story_tan_le  26.7M  22.6G  4.08K
                       older_people_are_happier_laura_carstensen  20.9M  22.7G  4.04K
                              we_can_recycle_plastic_mike_biddle  22.4M  22.7G  3.97K
                              print_your_own_medicine_lee_cronin  5.44M  22.7G  3.93K
                    how_to_look_inside_the_brain_carl_schoonover  9.04M  22.7G  3.89K
                  building_unimaginable_shapes_michael_hansmeyer  24.9M  22.7G  3.83K
    how_to_step_up_in_the_face_of_disaster_caitria_morgan_o_neil  19.7M  22.7G  3.77K
            a_prosthetic_eye_to_treat_blindness_sheila_nirenberg  19.1M  22.8G  3.66K
                         the_right_time_to_second_guess_yourself  22.4M  22.8G  3.55K
                                embrace_the_remix_kirby_ferguson  17.5M  22.8G  3.52K
                         how_you_can_help_fight_pediatric_cancer  14.4M  22.8G  3.51K
                           advice_to_young_scientists_e_o_wilson  27.0M  22.8G  3.44K
                   the_strange_politics_of_disgust_david_pizarro  27.5M  22.9G  3.37K
                             what_s_left_to_explore_nathan_wolfe  14.1M  22.9G  3.31K
      what_if_our_healthcare_system_kept_us_healthy_rebecca_onie  29.6M  22.9G  3.31K
          visualizing_the_medical_data_explosion_anders_ynnerman  25.7M  22.9G  3.26K
                       the_100000_student_classroom_peter_norvig  11.4M  22.9G  3.22K
         a_teacher_growing_green_in_the_south_bronx_stephen_ritz  31.5M  23.0G  3.21K
                         why_i_hold_on_to_my_grandmother_s_tales  13.0M  23.0G  3.21K
                               tracking_the_trackers_gary_kovacs  11.2M  23.0G  3.21K
                      fighting_with_non_violence_scilla_elworthy  13.8M  23.0G  3.19K
           why_architects_need_to_use_their_ears_julian_treasure  16.5M  23.0G  3.11K
                            what_s_your_200_year_plan_raghava_kk  20.8M  23.0G  2.92K
                 the_secret_lives_of_paintings_maurizio_seracini  21.8M  23.1G  2.91K
                  the_flavors_of_life_through_the_eyes_of_a_chef  17.4M  23.1G  2.91K
                                     life_s_third_act_jane_fonda  26.0M  23.1G  2.85K
                             be_an_artist_right_now_young_ha_kim  38.2M  23.1G  2.85K
                           making_sense_of_maps_aris_venetikidis  36.0M  23.2G  2.82K
                fighting_a_contagious_cancer_elizabeth_murchison  26.7M  23.2G  2.77K
       tracking_ancient_diseases_using_plaque_christina_warinner  9.05M  23.2G  2.74K
    experiments_that_point_to_a_new_understanding_of_cancer_mina  36.7M  23.3G  2.73K
                 cloudy_with_a_chance_of_joy_gavin_pretor_pinney  18.9M  23.3G  2.73K
                   design_for_people_not_awards_timothy_prestero  20.8M  23.3G  2.72K
                              the_art_of_creating_awe_rob_legato  50.3M  23.3G  2.56K
                  can_democracy_exist_without_trust_ivan_krastev  27.9M  23.4G  2.53K
           the_promise_of_research_with_stem_cells_susan_solomon  24.4M  23.4G  2.42K
                            a_census_of_the_ocean_paul_snelgrove  27.5M  23.4G  2.39K
                   finding_life_we_can_t_imagine_christoph_adami  41.4M  23.5G  2.38K
                      your_phone_company_is_watching_malte_spitz  27.3M  23.5G  2.32K
               welcome_to_the_genomic_revolution_richard_resnick  20.1M  23.5G  2.32K
                             technology_s_epic_story_kevin_kelly  31.7M  23.5G  2.28K
                freeing_energy_from_the_grid_justin_hall_tipping  30.8M  23.6G  2.21K
                       excuse_me_may_i_rent_your_car_robin_chase  31.3M  23.6G  2.14K
                     the_economic_injustice_of_plastic_van_jones  41.7M  23.6G  2.09K
      how_open_data_is_changing_international_aid_sanjay_pradhan  31.8M  23.7G  2.09K
                       a_girl_who_demanded_school_kakenya_ntaiya  44.2M  23.7G  2.06K
                      demand_a_fair_trade_cell_phone_bandi_mbubi  15.2M  23.7G  2.03K
             what_your_designs_say_about_you_sebastian_deterding  18.0M  23.7G  1.95K
                demand_a_more_open_source_government_beth_noveck  41.4M  23.8G  1.91K
                     a_story_about_knots_and_surgeons_ed_gavagan  24.7M  23.8G  1.84K
                       let_s_pool_our_medical_data_john_wilbanks  32.1M  23.8G  1.75K
             a_lab_the_size_of_a_postage_stamp_george_whitesides  26.3M  23.9G  1.65K
             a_test_for_parkinson_s_with_a_phone_call_max_little  12.5M  23.9G  1.65K
         ethical_riddles_in_hiv_research_boghuma_kabisen_titanji  20.8M  23.9G  1.64K
                 massive_scale_online_collaboration_luis_von_ahn  32.2M  23.9G  1.61K
                 a_short_intro_to_the_studio_school_geoff_mulgan  8.79M  23.9G  1.49K
           3_stories_of_local_eco_entrepreneurship_majora_carter  27.2M  24.0G  1.46K
                             put_a_value_on_nature_pavan_sukhdev  31.9M  24.0G  1.45K
                                   how_to_stop_torture_karen_tse  20.1M  24.0G  1.32K
    how_cyberattacks_threaten_real_world_peace_guy_philippe_gold  13.5M  24.0G  1.31K
               the_day_i_turned_down_tim_berners_lee_ian_ritchie  10.7M  24.0G  1.27K
    women_entrepreneurs_example_not_exception_gayle_tzemach_lemm  28.7M  24.1G  1.25K
                       the_arts_festival_revolution_david_binder  17.0M  24.1G  1.21K
                         filming_democracy_in_ghana_jarreth_merz  18.0M  24.1G  1.08K
                        there_are_no_scraps_of_men_alberto_cairo  36.4M  24.1G  1.07K
                   an_unexpected_place_of_healing_ramona_pierson  33.8M  24.2G  1.01K
                          digital_humanitarianism_paul_conneally  17.6M  24.2G  0.99K
                                life_in_biosphere_2_jane_poynter  27.7M  24.2G    937
                  the_economic_case_for_preschool_timothy_bartik  31.1M  24.2G    706
              let_s_crowdsource_the_world_s_goals_jamie_drummond  26.6M  24.3G    687



```python

```


```python

```
