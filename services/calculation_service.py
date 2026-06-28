from db.models import ItemConsumer, AufteilungsModus
from db.database import get_session
from sqlmodel import select


def recalculate_item_consumers(item_id: int):

    with get_session() as session:

        item = session.exec(
            select(ItemConsumer).where(ItemConsumer.item_id == item_id)
        ).all()

        if not item:
            return

        mode = item[0].modus

        # -------------------------
        # GLEICHMÄSSIG
        # -------------------------
        if mode == AufteilungsModus.GLEICHMAESSIG:

            count = len(item)
            if count == 0:
                return

            for c in item:
                c.wert = 1.0
                session.add(c)

        # -------------------------
        # PROZENT
        # -------------------------
        elif mode == AufteilungsModus.PROZENT:

            total = sum(c.wert for c in item)

            if total == 0:
                return

            # normalisieren auf 100%
            for c in item:
                c.wert = (c.wert / total) * 100
                session.add(c)

        # -------------------------
        # STÜCKZAHL
        # -------------------------
        elif mode == AufteilungsModus.STUECKZAHL:
            # NICHT automatisch verändern
            # nur Validierung wäre sinnvoll
            pass

        session.commit()
