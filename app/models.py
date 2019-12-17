from sqlalchemy.orm import backref
from sqlalchemy.schema import PrimaryKeyConstraint
from app import db

class Web(db.Model):
    __tablename__ = "webs"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, unique=True, nullable=False)
    last_updated = db.Column(db.DateTime)
    pages = db.relationship('Page', backref='web', lazy='dynamic')

    def __repr__(self):
        return '<Web {}>'.format(self.url)


class Page(db.Model):
    __tablename__ = "pages"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, unique=True, nullable=False)
    html = db.Column(db.Text)
    error = db.Column(db.Integer)
    old_rank = db.Column(db.Float)
    new_rank = db.Column(db.Float)
    web_id = db.Column(db.Integer, db.ForeignKey("webs.id"))

    def __repr__(self):
        return f"<Page url={self.url}, new_rank={self.new_rank}, web={self.web}>"


class Link(db.Model):
    __tablename__ = "links"
    from_id = db.Column(db.Integer, db.ForeignKey("pages.id"))
    to_id = db.Column(db.Integer, db.ForeignKey("pages.id", ondelete='CASCADE'))

    __table_args__ = (PrimaryKeyConstraint(from_id, to_id),)

    from_url = db.relationship("Page", foreign_keys=[from_id])
    to_url = db.relationship("Page", foreign_keys=[to_id], backref=backref("successors", passive_deletes=True))

    def __repr__(self):
        return f"<Link from {self.from_url} -to-> {self.to_url}>"
