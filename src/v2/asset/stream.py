import io
import os
import binascii


__all__ = [
    "extract_archive"
]


def extract_archive(path, output):
    table = {}
    buffer = io.BytesIO()
    # read file
    with open(path, "rb") as file:
        buffer.write(file.read())
    # read end record header
    buffer.seek(buffer.getbuffer().nbytes - 22)
    signature = buffer.read(4)
    if signature.hex() != "504b0506":
        raise ValueError("Invalid signature")
    _ = buffer.read(12)
    cd_offset = int.from_bytes(buffer.read(4), byteorder="little")
    # read files
    buffer.seek(cd_offset)
    while True:
        # read central directory header
        signature = buffer.read(4)
        if signature.hex() == "504b0506":
            break
        if signature.hex() != "504b0102":
            raise ValueError("Invalid signature")
        _           = buffer.read(24)
        filename_len = int.from_bytes(buffer.read(2), "little")
        _            = buffer.read(2)
        comment_len  = int.from_bytes(buffer.read(2), "little")
        _            = buffer.read(8)
        lfh_offset   = int.from_bytes(buffer.read(4), "little")
        end = buffer.tell() + filename_len + comment_len
        # read local file header
        buffer.seek(lfh_offset)
        signature = buffer.read(4)
        if signature.hex()  != "504b0304":
            raise Exception("Invalid signature")
        _        = buffer.read(10)
        checksum = int.from_bytes(buffer.read(4), "little")
        size     = int.from_bytes(buffer.read(4), "little")
        _        = buffer.read(8)
        filename = buffer.read(filename_len).decode("ascii")
        # print(f'"{filename[1:]}"', end=", ")
        data     = buffer.read(size)
        if binascii.crc32(data) != checksum:
            raise Exception("Invalid checksum")
        table[filename] = data
        buffer.seek(end)
    # write unarchived files
    for filename, data in table.items():
        path = os.path.join(output, filename[1:])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as file:
            file.write(data)


def create_archive(path, output, locale: str = "en"):
    target_files = {
        "en": (
            "Emotions.png,SearchButton.png,ReasonButton.png,EmblemsMOL.png,InkD"
            "enied.png,InkApproved.png,ReasonStampTop.png,GiveIcon.png,StampBot"
            "Approved.png,LoadDrag.png,FingerprintButton.png,RifleKill.png,Deta"
            "inButton.png,LoadDay.png,Upgrades.png,StampBotDenied.png,RifleTran"
            "q.png,InkReason.png,Filer.png,EmblemsMOA.png,LoadButtonNew.png,Apa"
            "rtmentClass.png,LoadButtonLatest.png,StampBarMid.png,News.png,intr"
            "o/Arstotzka.png,intro/Shutter.png,intro/Obrinspector.png,intro/Int"
            "ro1.png,intro/EndNews.png,papers/BrothelFlyerInner.png,papers/Bull"
            "etinInnerCorrelateTut.png,papers/LoveSongInner4.png,papers/Forgery"
            "FlyerInnerFront.png,papers/RulesInnerAsylumGrant.png,papers/Vaccin"
            "eCertInner.png,papers/PassportInnerImpor.png,papers/VisaSlipInner."
            "png,papers/RulesInnerRegionArstotzka.png,papers/PassportInnerArsto"
            "tzka.png,papers/RulesTabRulesL.png,papers/LoveSongInner2.png,paper"
            "s/PressPassInner.png,papers/LoveSongInner3.png,papers/BulletinInne"
            "rRuleTut.png,papers/RulesInnerDocs.png,papers/TranscriptInner.png,"
            "papers/PassportInnerRepublia.png,papers/LoveSongInner1.png,papers/"
            "RulesInnerLast.png,papers/WorkPermitInner.png,papers/DiplomaticAut"
            "hInner.png,papers/SpyDocsInnerBack.png,papers/ArskickersInner.png,"
            "papers/BizCardInnerBack.png,papers/PezpertInner.png,papers/RulesTa"
            "bMapR.png,papers/BulletinInnerNews.png,papers/RulesInnerEntryPermi"
            "t.png,papers/RuleIssuingCity.png,papers/RulesInnerWorkPermit.png,p"
            "apers/RulesTabConfL.png,papers/EntryPermitInner.png,papers/LocketI"
            "nnerOpen.png,papers/EntryTicketInner.png,papers/BulletinInnerBooth"
            "Tut.png,papers/FingerprintsInner.png,papers/PoliceBadgeInner.png,p"
            "apers/RulesTabDocsL.png,papers/BulletinInnerBoothTut2.png,papers/B"
            "ulletinInnerBoothTut3.png,papers/ForgeryFlyerInnerBack.png,papers/"
            "IdCardInner.png,papers/AccessPermitInner.png,papers/AsylumGrantInn"
            "er.png,papers/RulesUpgrade0.png,papers/BulletinInnerGunTut.png,pap"
            "ers/GymFlyerInner.png,papers/RulesUpgrade1.png,papers/RulesTabMapL"
            ".png,papers/VictimPhotoInnerBack.png,papers/PlaqueTwoInner.png,pap"
            "ers/RuleDiploAccess.png,papers/PassportInnerUnitedFed.png,papers/R"
            "ulesUpgrade3.png,papers/SonDrawingOuter.png,papers/RulesUpgrade2.p"
            "ng,papers/RulesTabConfR.png,papers/BulletinInnerFilerTut.png,paper"
            "s/PassportInnerAntegria.png,papers/PoisonInnerOpen1.png,papers/Rul"
            "esTabDocsR.png,papers/FamilyPhotoInner.png,papers/IdentityRecordIn"
            "ner.png,papers/PoisonInnerOpen2.png,papers/BulletinInnerDiploTut.p"
            "ng,papers/RulesInnerBooth3.png,papers/RulesUpgrade4.png,papers/Rul"
            "esInnerBooth2.png,papers/SonDrawingMount.png,papers/RulesInnerAcce"
            "ssPermit.png,papers/PassportInnerObristan.png,papers/BulletinInner"
            "TouchTut.png,papers/RulesInnerConfiscation.png,papers/SonDrawingIn"
            "ner.png,papers/EzicNoteInnerOpen.png,papers/RulesInnerVaccineCert."
            "png,papers/BulletinInnerCriminals.png,papers/RulesInnerIdCard.png,"
            "papers/IdSupplementInner.png,papers/BulletinInnerPassportTut.png,p"
            "apers/BulletinInnerMissingTut.png,papers/BizCardInnerFront.png,pap"
            "ers/HintMissingInner.png,papers/RulesInnerIdSupplement.png,papers/"
            "RulesInnerHome.png,papers/RulesTabRulesR.png,papers/RuleSealRequir"
            "ed.png,papers/PassportInnerKolechia.png,papers/SeizureSlipInner.pn"
            "g,papers/BrothelHelpInner.png,papers/RulesInnerBasic.png,papers/Bu"
            "lletinInnerContraTut.png,papers/RulesInnerBooth.png,papers/PoisonI"
            "nnerBack.png,papers/BulletinPagesNote.png,papers/RulesInnerRegion."
            "png,papers/CitationInner.png,papers/PlaqueOneInner.png,papers/Rule"
            "sInnerDiplomaticAuth.png,data/Text.xml,data/LocVersion.txt,data/Us"
            "edChars.txt,data/Loc.csv"
        ),
        "ko": (
            "Emotions.png,SearchButton.png,ReasonButton.png,EmblemsMOL.png,InkD"
            "enied.png,InkApproved.png,ReasonStampTop.png,GiveIcon.png,StampBot"
            "Approved.png,LoadDrag.png,FingerprintButton.png,RifleKill.png,Deta"
            "inButton.png,LoadDay.png,Upgrades.png,StampBotDenied.png,RifleTran"
            "q.png,InkReason.png,Filer.png,EmblemsMOA.png,LoadButtonNew.png,Apa"
            "rtmentClass.png,LoadButtonLatest.png,StampBarMid.png,News.png,intr"
            "o/Arstotzka.png,intro/Shutter.png,intro/Obrinspector.png,intro/Int"
            "ro1.png,intro/EndNews.png,papers/BrothelFlyerInner.png,papers/Bull"
            "etinInnerCorrelateTut.png,papers/LoveSongInner4.png,papers/Forgery"
            "FlyerInnerFront.png,papers/RulesInnerAsylumGrant.png,papers/Vaccin"
            "eCertInner.png,papers/PassportInnerImpor.png,papers/VisaSlipInner."
            "png,papers/RulesInnerRegionArstotzka.png,papers/PassportInnerArsto"
            "tzka.png,papers/RulesTabRulesL.png,papers/LoveSongInner2.png,paper"
            "s/PressPassInner.png,papers/LoveSongInner3.png,papers/BulletinInne"
            "rRuleTut.png,papers/RulesInnerDocs.png,papers/TranscriptInner.png,"
            "papers/PassportInnerRepublia.png,papers/LoveSongInner1.png,papers/"
            "RulesInnerLast.png,papers/WorkPermitInner.png,papers/DiplomaticAut"
            "hInner.png,papers/SpyDocsInnerBack.png,papers/ArskickersInner.png,"
            "papers/BizCardInnerBack.png,papers/PezpertInner.png,papers/RulesTa"
            "bMapR.png,papers/BulletinInnerNews.png,papers/RulesInnerEntryPermi"
            "t.png,papers/RuleIssuingCity.png,papers/RulesInnerWorkPermit.png,p"
            "apers/RulesTabConfL.png,papers/EntryPermitInner.png,papers/LocketI"
            "nnerOpen.png,papers/EntryTicketInner.png,papers/BulletinInnerBooth"
            "Tut.png,papers/FingerprintsInner.png,papers/PoliceBadgeInner.png,p"
            "apers/RulesTabDocsL.png,papers/BulletinInnerBoothTut2.png,papers/B"
            "ulletinInnerBoothTut3.png,papers/ForgeryFlyerInnerBack.png,papers/"
            "IdCardInner.png,papers/AccessPermitInner.png,papers/AsylumGrantInn"
            "er.png,papers/RulesUpgrade0.png,papers/BulletinInnerGunTut.png,pap"
            "ers/GymFlyerInner.png,papers/RulesUpgrade1.png,papers/RulesTabMapL"
            ".png,papers/VictimPhotoInnerBack.png,papers/PlaqueTwoInner.png,pap"
            "ers/RuleDiploAccess.png,papers/PassportInnerUnitedFed.png,papers/R"
            "ulesUpgrade3.png,papers/SonDrawingOuter.png,papers/RulesUpgrade2.p"
            "ng,papers/RulesTabConfR.png,papers/BulletinInnerFilerTut.png,paper"
            "s/PassportInnerAntegria.png,papers/PoisonInnerOpen1.png,papers/Rul"
            "esTabDocsR.png,papers/FamilyPhotoInner.png,papers/IdentityRecordIn"
            "ner.png,papers/PoisonInnerOpen2.png,papers/BulletinInnerDiploTut.p"
            "ng,papers/RulesInnerBooth3.png,papers/RulesUpgrade4.png,papers/Rul"
            "esInnerBooth2.png,papers/SonDrawingMount.png,papers/RulesInnerAcce"
            "ssPermit.png,papers/PassportInnerObristan.png,papers/BulletinInner"
            "TouchTut.png,papers/RulesInnerConfiscation.png,papers/SonDrawingIn"
            "ner.png,papers/EzicNoteInnerOpen.png,papers/RulesInnerVaccineCert."
            "png,papers/BulletinInnerCriminals.png,papers/RulesInnerIdCard.png,"
            "papers/IdSupplementInner.png,papers/BulletinInnerPassportTut.png,p"
            "apers/BulletinInnerMissingTut.png,papers/BizCardInnerFront.png,pap"
            "ers/HintMissingInner.png,papers/RulesInnerIdSupplement.png,papers/"
            "RulesInnerHome.png,papers/RulesTabRulesR.png,papers/RuleSealRequir"
            "ed.png,papers/PassportInnerKolechia.png,papers/SeizureSlipInner.pn"
            "g,papers/BrothelHelpInner.png,papers/RulesInnerBasic.png,papers/Bu"
            "lletinInnerContraTut.png,papers/RulesInnerBooth.png,papers/PoisonI"
            "nnerBack.png,papers/BulletinPagesNote.png,papers/RulesInnerRegion."
            "png,papers/CitationInner.png,papers/PlaqueOneInner.png,papers/Rule"
            "sInnerDiplomaticAuth.png,fonts/notnokia_u_regular_8.png,fonts/chix"
            "a_demibold_14.fnt,fonts/chixa_demibold_14.png,fonts/notnokia_u_reg"
            "ular_8.fnt,fonts/pixelplay_regular_16.fnt,fonts/minikylie_u_regula"
            "r_8.png,fonts/pixelplay_regular_16.png,fonts/minikylie_u_regular_8"
            ".fnt,fonts/atarismall_u_regular_8.png,fonts/5mikropix_regular_8.pn"
            "g,fonts/atarismall_u_regular_8.fnt,fonts/5mikropix_regular_8.fnt,f"
            "onts/motorolascreentype_u_regular_16.fnt,fonts/04b03_u_regular_8.p"
            "ng,fonts/bmmini_u_regular_8.png,fonts/resource_u_regular_8.fnt,fon"
            "ts/motorolascreentype_u_regular_16.png,fonts/04b03_u_regular_8.fnt"
            ",fonts/resource_u_regular_8.png,fonts/bmmini_u_regular_8.fnt,data/"
            "Text.xml,data/LocVersion.txt,data/UsedChars.txt,data/Loc.csv"
        )
    }
    table = {}
    buffer = io.BytesIO()
    # read files
    for filename in target_files[locale].split(","):
        filepath = os.path.join(path, filename)
        with open(filepath, "rb") as file:
            table[f"/{filename}"] = [file.read(), 0]
    # write local file header
    for filename, (data, _) in table.items():
        table[filename][1] = buffer.tell()
        header = bytearray()
        header += b"\x50\x4b\x03\x04"
        header += b"\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        header += binascii.crc32(data).to_bytes(4, "little")
        header += len(data).to_bytes(4, "little")
        header += len(data).to_bytes(4, "little")
        header += len(filename).to_bytes(2, "little")
        header += b"\x00\x00"
        header += filename.encode("ascii")
        buffer.write(header)
        buffer.write(data)
    # write central directory header
    cdh_offset = buffer.tell()
    total_cdh_size = 0
    for filename, (data, offset) in table.items():
        header = bytearray()
        header += b"\x50\x4b\x01\x02"
        header += b"\x14\x00\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        header += binascii.crc32(data).to_bytes(4, "little")
        header += len(data).to_bytes(4, "little")
        header += len(data).to_bytes(4, "little")
        header += len(filename).to_bytes(2, "little")
        header += b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        header += offset.to_bytes(4, "little")
        header += filename.encode("ascii")
        buffer.write(header)
        total_cdh_size += len(header)
    # write end record header
    header = bytearray()
    header += b"\x50\x4b\x05\x06"
    header += b"\x00\x00\x00\x00"
    header += len(table).to_bytes(2, "little")
    header += len(table).to_bytes(2, "little")
    header += total_cdh_size.to_bytes(4, "little")
    header += cdh_offset.to_bytes(4, "little")
    header += b"\x00\x00"
    buffer.write(header)
    # write archive
    buffer.seek(0)
    os.makedirs(os.path.dirname(output), exist_ok=True)
    with open(output, "wb") as file:
        file.write(buffer.read())
