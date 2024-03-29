from __future__ import annotations
from functools import reduce
import os
from pathlib import Path
from typing import Any, List

from databases import Database
from Models.Admin import AdminInDatabase
from Models.Images import ImageWithAllInfo, ImageWithAllInfoInDatabase, SectionInDatabase, SectionWithAllInfo, SectionWithAllInfoInDatabase, TagInDatabase
from Utils import *
from Utils.Env import EnvClass

class DatabaseError(Exception): pass
class UserExists(DatabaseError): pass
class UserNotExists(DatabaseError): pass
class PhotoNotExists(DatabaseError): pass
class CommentNotExists(DatabaseError): pass

class DatabaseConnectionError(DatabaseError): pass
class DatabaseTransactionError(DatabaseError): pass

class DatabaseBaseClass:
    def __init__(self):
        self.path_to_database = "database.db"
        self.database_inited: bool = False
        self.Hasher = Hasher.HasherClass()
        self.database: Database | None = None
        self.Env = EnvClass()
        

    async def database_init(self):
        self.database = Database(self.Env.env["GALLERY_DATABASE_URL"])
        await self.database.connect()
        self.database_inited = True
        try:
            await self.request(
                'CREATE TABLE IF NOT EXISTS admin('\
                '    hashOfPassword TEXT PRIMARY KEY,'\
                '    aboutMe TEXT UNIQUE,'\
                '    avatar TEXT);'
            )
            await self.request(
                'CREATE TABLE IF NOT EXISTS images('\
                '    imageId INTEGER PRIMARY KEY AUTOINCREMENT,'\
                '    image TEXT NOT NULL);'
            )
            await self.request(
                'CREATE TABLE IF NOT EXISTS images_to_tags('\
                '    imageId INTEGER,'\
                '    tagId INTEGER, '\
                '    UNIQUE("imageId","tagId"));'
            )
            await self.request(
                'CREATE TABLE IF NOT EXISTS tags('\
                '    tagId INTEGER PRIMARY KEY AUTOINCREMENT,'\
                '    tag TEXT);'
            )
            await self.request(
                'CREATE TABLE IF NOT EXISTS tags_to_sections('\
                '    tagId INTEGER,'\
                '    sectionId INTEGER, '\
                '    UNIQUE("tagId","sectionId"));'
            )
            await self.request(
                'CREATE TABLE IF NOT EXISTS sections('\
                '    sectionId INTEGER PRIMARY KEY AUTOINCREMENT,'\
                '    section TEXT);'
            )
            hashOfPassword = await self.request("SELECT hashOfPassword FROM admin")
            if(hashOfPassword and hashOfPassword[0]["hashOfPassword"]): ...
            else:
                await self.request('INSERT INTO admin(hashOfPassword) VALUES(:hash);', \
                        hash=self.Hasher.PasswordHash(self.Env.env["GALLERY_ADMIN_PASSWORD"]))
        except Exception as e:
            print(e)
            self.database_inited = False
        finally:
            return self.database_inited

    async def database_uninit(self):
        if(self.database): await self.database.disconnect()

    async def request(self, request: str, *args: dict[str, str | int], **other: str | int):
        if(not self.database_inited or self.database == None):
            if(not await self.database_init()):
                raise DatabaseConnectionError()
        try:
            common_dict = {key: value for dict in [*args, other] for key, value in dict.items()}
            if("select" not in request.lower()):
                await self.database.execute(request, common_dict) #type: ignore
                return None
            else:
                response: list[dict[str, Any]] = \
                    list(map(
                        lambda x: dict(x), #type: ignore
                        await self.database.fetch_all(request, common_dict) #type: ignore
                    ))
                return response
        except Exception as e:
            print(f"Request error - {e}")
            raise DatabaseTransactionError()

    def imagesFromDatabaseToJson(self, images_from_database: List[ImageWithAllInfoInDatabase]) -> list[ImageWithAllInfo]:
        images: List[ImageWithAllInfo] = []
        if(not images_from_database): return []
        image_info: List[ImageWithAllInfoInDatabase] = []
        for image_in_database_line in images_from_database:
            if(len(image_info) > 0 and image_in_database_line["imageId"] != image_info[-1]["imageId"]):
                images.append(self.imageFromDatabaseToJson(image_info))
                image_info = []
            image_info.append(image_in_database_line)
        images.append(self.imageFromDatabaseToJson(image_info))
        return images

    def imageFromDatabaseToJson(self, image_from_database: list[ImageWithAllInfoInDatabase]) -> ImageWithAllInfo: 
        image: ImageWithAllInfo = ImageWithAllInfo(
            imageId=image_from_database[0]["imageId"],
            image=image_from_database[0]["image"],
            tags=[],
            sections=[]
        )
        for image_info in image_from_database:
            if(image_info["tagId"]):
                addedTags = [tag.tagId for tag in image["tags"]]
                if(image_info["tagId"] not in addedTags):
                    image["tags"].append(
                        TagInDatabase(
                            tagId=image_info["tagId"], 
                            tag=image_info["tag"]
                            )
                        )
            if(image_info["sectionId"]):
                addedSections = [section.sectionId for section in image["sections"]]
                if(image_info["sectionId"] not in addedSections):
                    image["sections"].append(
                        SectionInDatabase(
                            sectionId=image_info["sectionId"], 
                            section=image_info["section"]
                        )
                    )
        return image

    def sectionsFromDatabaseToJson(self, sections_from_database: List[SectionWithAllInfoInDatabase]) -> list[SectionWithAllInfo]:
        sections: List[SectionWithAllInfo] = []
        if(not sections_from_database): return []
        section_info: List[SectionWithAllInfoInDatabase] = []
        for section_in_database_line in sections_from_database:
            if(len(section_info) > 0 and section_in_database_line["sectionId"] != section_info[-1]["sectionId"]):
                sections.append(self.sectionFromDatabaseToJson(section_info))
                section_info = []
            section_info.append(section_in_database_line)
        sections.append(self.sectionFromDatabaseToJson(section_info))
        return sections

    def sectionFromDatabaseToJson(self, section_from_database: list[SectionWithAllInfoInDatabase]) -> SectionWithAllInfo: 
        section: SectionWithAllInfo = SectionWithAllInfo(
            sectionId=section_from_database[0]["sectionId"],
            section=section_from_database[0]["section"],
            tags=[],
        )
        for section_info in section_from_database:
            if(section_info["tagId"]):
                addedTags = [tag.tagId for tag in section["tags"]]
                if(section_info["tagId"] not in addedTags):
                    section["tags"].append(
                        TagInDatabase(
                            tagId=section_info["tagId"], 
                            tag=section_info["tag"]
                            )
                        )
        return section


class DatabaseClass(DatabaseBaseClass):

    # --- REQUESTS ---

    getAdminRequest = "SELECT * FROM admin"
    getPasswordRequest = "SELECT hashOfPassword FROM admin"
    getInfoRequest = "SELECT aboutMe FROM admin"
    editInfoRequest = "UPDATE admin set aboutMe=:aboutMe"
    createSectionRequest = "INSERT INTO sections(section, includedTags) VALUES(:section, :includedTags);"
    deleteSectionRequest = "DELETE FROM sections WHERE sectionId=:sectionId"

    # - ADMIN INFO -
    # - IMAGES -
    getAllImagesRequest = "SELECT images.*, tags.*, sections.* FROM images "\
                    "LEFT OUTER JOIN images_to_tags itt ON itt.imageId = images.imageId "\
                    "LEFT OUTER JOIN tags ON itt.tagId = tags.tagId "\
                    "LEFT OUTER JOIN tags_to_sections tts ON tts.tagId = tags.tagId "\
                    "LEFT OUTER JOIN sections ON sections.sectionId = tts.sectionId "\
                    "ORDER BY images.imageId"
    getSectionImagesRequest = "SELECT images.*, tags.*, sections.* FROM images "\
                    "LEFT OUTER JOIN images_to_tags itt ON itt.imageId = images.imageId "\
                    "LEFT OUTER JOIN tags ON itt.tagId = tags.tagId "\
                    "LEFT OUTER JOIN tags_to_sections tts ON tts.tagId = tags.tagId "\
                    "LEFT OUTER JOIN sections ON sections.sectionId = tts.sectionId "\
                    "WHERE sections.sectionId = :sectionId ORDER BY images.imageId"
    getImageById = "SELECT images.*, tags.*, sections.* FROM images "\
                    "LEFT OUTER JOIN images_to_tags itt ON itt.imageId = images.imageId "\
                    "LEFT OUTER JOIN tags ON itt.tagId = tags.tagId "\
                    "LEFT OUTER JOIN tags_to_sections tts ON tts.tagId = tags.tagId "\
                    "LEFT OUTER JOIN sections ON sections.sectionId = tts.sectionId "\
                    "WHERE images.imageId=:imageId" #TODO: getAllImagesRequest + "WHERE..." 
    addImageRequest = "INSERT INTO images(image) VALUES(:image);"
    getLastImageId = "SELECT MAX(imageId) FROM images"
    addTagToImageRequest = "INSERT or IGNORE INTO images_to_tags VALUES(:imageId, :tagId);"
    deleteTagFromImageRequest = "DELETE FROM images_to_tags WHERE imageId=:imageId AND tagId=:tagId;"

    # - TAGS -
    getTagsRequest = "SELECT * FROM tags"
    editTagNameRequest = 'UPDATE tags SET tag=:edited_name WHERE tagId=:tagId'
    createTagRequest = "INSERT INTO tags(tag) VALUES(:tag);"
    deleteTagRequest = "DELETE FROM tags WHERE tagId=:tagId"
    getLastTagId = "SELECT MAX(tagId) FROM tags"

    # - SECTIONS -
    getSectionsRequest = "SELECT sections.*, tags.* FROM sections "\
                         "LEFT OUTER JOIN tags_to_sections tts ON tts.sectionId = sections.sectionId "\
                         "LEFT OUTER JOIN tags ON tags.tagId = tts.tagId "
    addTagToSectionRequest = "INSERT or IGNORE INTO tags_to_sections VALUES(:tagId, :sectionId);"
    deleteTagFromSectionRequest = "DELETE FROM tags_to_sections WHERE sectionId=:sectionId AND tagId=:tagId;"
    changeSectionNameRequest = "UPDATE sections SET section=:section WHERE sectionId=:sectionId"

    # --- FUNCTIONS ---

    # - ADMIN INFO -
    async def get_admin(self) -> AdminInDatabase | None:
        response: List[AdminInDatabase] | None \
                = await self.request(self.getAdminRequest) #type: ignore
        return response[0] if response and len(response)>0 else None

    async def get_password(self) -> str:
        password = await self.request(self.getPasswordRequest)
        return password[0]["hashOfPassword"] # type: ignore - there is always a password

    async def get_info(self) -> str:
        info = await self.request(self.getInfoRequest)
        return info[0] 

    async def edit_info(self, info: str) -> None:
        await self.request(self.editInfoRequest, {"aboutMe": info})

    # - TAGS -
    async def create_tag(self, tag: str) -> int:
        await self.request(self.createTagRequest, tag=tag)
        newTagIdRequestResult = await self.request(self.getLastTagId)
        if(newTagIdRequestResult is None): raise DatabaseError()
        return newTagIdRequestResult[0]["MAX(tagId)"]

    async def delete_tag(self, tagId: int) -> None:
        await self.request(self.deleteTagRequest, tagId=tagId)

    async def edit_tag_name(self, tagId: int, edited_name: str):
        await self.request(self.editTagNameRequest, {'tagId': tagId, 'edited_name': edited_name})

    async def get_tags(self) -> list[TagInDatabase]:
        tags: List[TagInDatabase] | None \
            = await self.request(self.getTagsRequest) #type: ignore
        return tags if tags else []

    # - SECTIONS -
    async def get_sections(self) -> list[SectionWithAllInfo]:
        sections: List[SectionWithAllInfoInDatabase] | None \
            = await self.request(self.getSectionsRequest) #type: ignore
        return self.sectionsFromDatabaseToJson(sections) if sections else []

    async def add_tag_to_section(self, sectionId: int, tagId: int):
        await self.request(self.addTagToSectionRequest, sectionId=sectionId, tagId=tagId)

    async def delete_tag_from_section(self, sectionId: int, tagId: int):
        await self.request(self.deleteTagFromSectionRequest, sectionId=sectionId, tagId=tagId)

    async def change_section_name(self, sectionId: int, sectionName: str):
        await self.request(self.changeSectionNameRequest, sectionId=sectionId, section=sectionName)

    #async def create_section(self, section: str, includedTagsList) -> None:
    #    includedTags = ";".join(includedTagsList)
    #    await self.request(self.createSectionRequest, {"section": section, "includedTags": includedTags})
    #async def delete_section(self, sectionId: int) -> None:
    #    await self.request(self.deleteSectionRequest, {"sectionId": sectionId})

    # - IMAGES -
    async def get_all_images(self) -> List[ImageWithAllInfo]:
        images: List[ImageWithAllInfoInDatabase] | None \
                = await self.request(self.getAllImagesRequest) #type: ignore
        return self.imagesFromDatabaseToJson(images) if images else []

    async def get_section_images(self, sectionId: int) -> List[ImageWithAllInfo]:
        images: List[ImageWithAllInfoInDatabase] | None \
                = await self.request(self.getSectionImagesRequest, sectionId=sectionId) #type: ignore
        return self.imagesFromDatabaseToJson(images) if images else []

    async def get_image(self, imageId: int) -> ImageWithAllInfo | None:
        images: List[ImageWithAllInfoInDatabase] | None \
                = await self.request(self.getImageById, imageId=imageId) #type: ignore
        return self.imagesFromDatabaseToJson(images)[0] if images else None

    async def add_image(self, filePath: str) -> int:
        await self.request(self.addImageRequest, image=filePath)
        newImageIdRequestResult = await self.request(self.getLastImageId)
        if(newImageIdRequestResult is None): raise DatabaseError()
        return newImageIdRequestResult[0]["MAX(imageId)"]

    async def add_tag_to_image(self, imageId: int, tagId: int):
        await self.request(self.addTagToImageRequest, imageId=imageId, tagId=tagId)

    async def delete_tag_from_image(self, imageId: int, tagId: int):
        await self.request(self.deleteTagFromImageRequest, imageId=imageId, tagId=tagId)