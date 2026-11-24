"""Aurora conversation and journal resources for the guardian of the Last Step."""

from aurora import Record, bite, dword, loc, lst, ref, string, word


def conversation(*, group=False):
    entries = []
    replies = []

    def address(solo, party):
        return party if group else solo

    def link(index, condition=''):
        return Record(0, Index=dword(index), Active=ref(condition), IsChild=bite(0))

    def entry(text):
        index = len(entries)
        entries.append(Record(0, Text=loc(text), Delay=dword(0), Comment=string(''),
                              Script=ref(''), Animation=dword(0), Speaker=string(''),
                              Sound=ref(''), Quest=string(''), RepliesList=lst([])))
        return index

    def reply(parent, text, *, to=None, action=''):
        index = len(replies)
        replies.append(Record(0, Text=loc(text), Delay=dword(0), Comment=string(''),
                              Script=ref(action), Animation=dword(0), Sound=ref(''), Quest=string(''),
                              EntriesList=lst([] if to is None else [link(to)])))
        entries[parent].value('RepliesList').append(link(index))

    greeting = entry(
        'Zde končí cesta, kterou smí projít poutníci z hory. Za tímto stupněm začíná nebeské '
        'předměstí a mé přísaze byl svěřen jeho práh. ' + address(
            'Nemáš znamení k přijetí. Přesto je za tebou dlouhá cesta. Vyslechnu, s čím chceš odejít.',
            'Nemáte znamení k přijetí. Přesto jste přišli daleko. Vyslechnu, s čím chcete odejít.'))
    mercy = entry(address(
        'Sejdi stejnou cestou a měj klidný krok. Za tento práh už nepokračuj.',
        'Sejděte stejnou cestou a mějte klidný krok. Za tento práh už nepokračujte.'))
    duel = entry(
        'Dlouhé věky zde měřím čas podle kroků větru. ' + address(
            'Dnes přede mnou stojí někdo, kdo ví, proč tasí. '
            'Nabízím ti zkoušku pod přísahou. Budu stát sám. Skloním čepel, jakmile prokážeš svou zdatnost.',
            'Dnes přede mnou stojí družina, která ví, proč tasí. '
            'Nabízím vám zkoušku pod přísahou. Budu stát sám. Skloním čepel, jakmile prokážete svou zdatnost.')
        + ' Po dobu zkoušky zůstane lucerna temná.')
    challenge = entry(
        address('Volíš-li průchod silou, zříkáš se ochrany zkoušky. ',
                'Volíte-li průchod silou, zříkáte se ochrany zkoušky. ') + 'Poslední lucerna '
        'se rozhoří a Jízda Valkýr stojí na mé zavolání. Práh budu hájit bez ústupků.')
    offer = entry(
        address('Zkoušku máš za sebou se ctí. Tvá ruka je pevná a víš, kdy šetřit čepel. Nyní ti svěřím práci hodnou ',
                'Obstáli jste. Máte pevnou ruku a víte, kdy šetřit čepel. Nyní vám svěřím práci hodnou ')
        + 'nebeské hlídky. Sesuv přerušil vedení z Filtrovny světla. Od té doby se na stezce rodí větrná těla. '
        + address('Vezmi můj klíč. ', 'Vezměte můj klíč. ')
        + 'Odemkne kamenné dveře ve východní části Chodeb clon. Sběrná čočka stále přijímá denní světlo. '
        + address(
            'Veď je kolem závalu, projdi průrvou a slož barvu pro ochrannou lucernu. Až se rozsvítí purpurová kontrolka na tabulce, přines mi zprávu.',
            'Veďte je kolem závalu, projděte průrvou a složte barvu pro ochrannou lucernu. Až se rozsvítí purpurová kontrolka na tabulce, přineste mi zprávu.'))
    repair = entry(
        address(
            'Mým klíčem odemkneš dveře ve východní chodbě. Ve Filtrovně sleduj paprsek až do Sálu skládání.',
            'Mým klíčem odemknete dveře ve východní chodbě. Ve Filtrovně sledujte paprsek až do Sálu skládání.')
        + ' Horní znak na tabulce ukazuje zapojené čidlo. Zelený čtverec potvrdí otevření clony a purpurový znak doručení světla.')
    done = entry(
        'Purpurové světlo dorazilo a stezka je zase chráněná. '
        + address('Přijmi dík nebeské hlídky. Ze schránek u lucerny si vyber jeden kus výstroje. ',
                  'Přijměte dík nebeské hlídky. Každý z vás si smí ze schránek u lucerny vybrat jeden kus výstroje. ')
        + 'Zbraň, zbroj, róbu, helmici, prsten nebo amulet.')
    paid = entry('Lucerna svítí a má přísaha trvá. ' + address(
        'Schránky jsem ti zpřístupnil. Sestup k hoře v pokoji.',
        'Schránky jsem vám zpřístupnil. Sestupte k hoře v pokoji.'))

    reply(greeting, address('Respektuji tvou přísahu. Odejdu v pokoji.', 'Respektujeme tvou přísahu. Odejdeme v pokoji.'), to=mercy)
    reply(greeting, address('Žádám čestnou zkoušku pod tvým dohledem.', 'Žádáme čestnou zkoušku pod tvým dohledem.'), to=duel)
    reply(greeting, address('Vynutím si cestu silou.', 'Vynutíme si cestu silou.'), to=challenge)
    reply(duel, address('Přijímám podmínky zkoušky.', 'Přijímáme podmínky zkoušky.'), action='hvd_duel')
    reply(duel, address('Sestoupím zpátky k hoře.', 'Sestoupíme zpátky k hoře.'), to=mercy)
    reply(challenge, address('I tak tasím.', 'I tak tasíme.'), action='hvd_challenge')
    reply(challenge, address('Zbraň zůstane v pochvě. Odejdu.', 'Zbraně zůstanou v pochvách. Odejdeme.'), to=mercy)
    reply(offer, address('Přijímám úkol a beru klíč.', 'Přijímáme úkol a bereme klíč.'), action='hvd_quest_take')
    reply(offer, address('Nechám si čas na rozmyšlenou.', 'Necháme si čas na rozmyšlenou.'))
    reply(done, address('Hlásím dokončení opravy.', 'Hlásíme dokončení opravy.'), action='hvd_quest_claim')
    reply(repair, address('Potřebuji klíč k servisním dveřím.', 'Potřebujeme klíč k servisním dveřím.'), action='hvd_quest_take')
    reply(repair, address('Vrátím se, až se lucerna rozsvítí.', 'Vrátíme se, až se lucerna rozsvítí.'))
    starts = [(paid,'hvd_dlg_paid'), (done,'hvd_dlg_done'), (repair,'hvd_dlg_work'),
              (offer,'hvd_dlg_offer'), (greeting,'hvd_dlg_idle')]
    return Record(DelayEntry=dword(0), DelayReply=dword(0), NumWords=dword(0), EndConversation=ref(''),
                  EndConverAbort=ref(''), EntryList=lst(entries), ReplyList=lst(replies),
                  StartingList=lst([Record(0, Index=dword(index), Active=ref(condition))
                                    for index, condition in starts]))


def journal():
    texts = (
        (10, False, 'Ithrenův klíč otevře kamenné dveře ve východní části Chodeb clon. Denní světlo ve Filtrovně '
                    'povedu kolem suti, projdu průrvou a v Sále skládání napojím světlovod ochranné lucerny.'),
        (20, False, 'Purpurové světlo dosáhlo Poslední lucerny. Další větrní elementálové se v této výpravě netvoří. Vrátím se k Ithrenovi '
                    'na Poslední stupeň.'),
        (30, True, 'Ithren přijal zprávu o opravě a otevřel schránky s výstrojí u lucerny. Můžu si z nich vybrat jeden předmět.'),
    )
    entries = [Record(0, ID=dword(stage), End=word(done), Text=loc(text))
               for stage, done, text in texts]
    return Record(Categories=lst([Record(0, Tag=string('hvd_clona_quest'),
                                         Name=loc('Světlo pro ochrannou clonu'),
                                         Priority=dword(0), XP=dword(0), Picture=word(65535),
                                         Comment=string(''), EntryList=lst(entries))]))
